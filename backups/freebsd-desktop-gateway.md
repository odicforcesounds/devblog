# FreeBSD desktop and gateway — runbook from first boot

A step-by-step build for one machine that is both a daily-driver desktop and the
router/firewall for the network behind it. Installation is deliberately out of
scope: this starts at the first boot of an installed system and ends with a
hardened host, a working i3 desktop, and isolated jails and VMs.

Written against FreeBSD 14.3 and 15.x. Commands that differ between the two are
marked. Verify with `freebsd-version -kru` before you start.

---

## 1. The machine

| Item | Value used in this document | Note |
| --- | --- | --- |
| CPU | Intel, 6 cores / 12 threads | SMT is turned off in phase 2, so the host ends with 6 usable CPUs |
| RAM | 16 GiB | ZFS ARC capped at 6 GiB, the rest stays for i3, Chromium, jails |
| GPU | NVIDIA discrete | Proprietary driver, X11 only; the Intel iGPU is disabled in firmware |
| NIC 1 | `em0` — WAN | DHCP from the ISP unless your line needs PPPoE |
| NIC 2 | `igc0` — LAN | Static `10.20.0.1/24` |
| Storage | ZFS root on UEFI/GPT | Boot environments available; swap encrypted at boot |
| Desktop | i3, xterm, Chromium | No display manager, no desktop environment |
| Roles | workstation, IPv4 router/NAT, DNS, DHCP, jail and VM host | IPv6 is left unconfigured and blocked |

Rename the interfaces in every file below if `ifconfig -l` shows different names.
The rest of the document assumes:

| Network | Subnet | Host address | Purpose |
| --- | --- | --- | --- |
| LAN | `10.20.0.0/24` | `10.20.0.1` | wired clients, DHCP pool `.100–.200` |
| Jails | `10.30.0.0/24` | `10.30.0.1` | internal bridge, no physical member |
| VMs | `10.40.0.0/24` | `10.40.0.1` | internal bridge, no physical member |
| WireGuard | `10.99.0.0/24` | `10.99.0.1` | optional remote access |

`admin` is the only interactive account. `wheel` is the only privileged group.

## 2. Design rules

1. **Default deny, everywhere.** pf ends in a block, jails get no mount rights,
   sshd listens on one address, DHCP hands out one pool.
2. **Remove before you harden.** A service that is not enabled cannot be
   exploited. Phase 9 deletes more attack surface than every sysctl combined.
3. **Isolation is layered, not replaced.** pf, MAC, Capsicum, jails and bhyve
   are independent layers. None of them is trusted to be the only one.
4. **Boot-time state beats runtime state.** Kernel modules load from
   `loader.conf`, the securelevel is raised once, and a boot environment exists
   before every change.
5. **Every hardening knob has a cost.** Each one below names what it breaks.
   If you cannot state the cost, you have not finished reading the step.
6. **Measure, then keep.** Performance changes go in one at a time, with the
   command that shows the difference. No folklore tunables.

## 3. Threat model

| Threat | Primary control | Residual risk |
| --- | --- | --- |
| Scanning and exploit attempts from the WAN | pf default-deny, no forwarded ports except one jail, no SSH on WAN | a kernel or driver 0-day in an exposed service |
| Malicious client on the LAN | client isolated from the gateway's services, only DNS/SSH/ICMP reach the host; LAN-to-jail traffic limited to 80/443 | ARP spoofing inside the LAN (see phase 6, static ARP option) |
| Compromised service in a jail | vnet jail, no mount rights, `securelevel=2`, rctl caps, pf blocks jail→LAN and jail→jail | shared FreeBSD kernel: a kernel exploit escapes any jail |
| Drive-by browser compromise | Chromium's Capsicum sandbox, `unprivileged_proc_debug=0`, W^X, ASLR, no Linuxulator | the NVIDIA blob and Chromium itself are large binary attack surfaces |
| Side-channel leakage between SMT siblings | SMT disabled (`kern.smp.hyperthreading_allowed=0`) plus microcode | firmware and DRAM-level attacks |
| Theft of the machine | encrypted swap, encrypted data datasets | an unencrypted boot pool reveals kernel and configuration, not data |
| Malicious VM guest | bhyve with virtio only, no passthrough, dedicated bridge | bhyve is not a security boundary against a hostile guest with a kernel bug |
| Local privilege escalation | W^X, ASLR, `security.bsd.*`, doas instead of su, tight file modes | any unpatched local kernel bug |
| Supply chain in packages | signed pkg repository, `pkg audit` daily, quarterly branch | the port itself |

What this build does **not** protect against: a compromised firmware/ME, DMA
attacks over Thunderbolt without IOMMU isolation, a malicious NVIDIA driver
update, or physical access to an unencrypted boot pool. Say so out loud before
calling the machine "secure".

## 4. Safety rails, before the first change

Everything below is applied over an SSH session or a console. Both can lock you
out. Do these four things first, once, and keep them for the whole build.

**4.1 Confirm you have a real console.** A monitor and keyboard on the machine,
or serial. If the only access is SSH, stop and connect a console; pf and sshd
changes below can and will cut the session.

**4.2 Know the two escape hatches.**

```sh
pfctl -d                 # disable pf entirely, immediately
pfctl -f /etc/pf.conf    # reload after a fix
```

`pfctl -d` is the reason to keep a console: it is one command, needs no network,
and survives a broken ruleset.

**4.3 Record a baseline** into `/root/baseline/` so later phases can prove what
changed:

```sh
mkdir -p /root/baseline
uname -a > /root/baseline/uname.txt
sysctl -a > /root/baseline/sysctl.before.txt
kldstat > /root/baseline/kldstat.before.txt
ifconfig -a > /root/baseline/ifconfig.before.txt
zpool status > /root/baseline/zpool.before.txt
zfs list > /root/baseline/zfs.before.txt
pkg info > /root/baseline/pkg.before.txt
service -e > /root/baseline/services.before.txt
pfctl -sr > /root/baseline/pf.before.txt 2>/dev/null || true
```

**4.4 Create a boot environment now.** With a ZFS root, this is the cheapest
undo in the system:

```sh
bectl create clean-install
bectl list
```

If a phase goes wrong badly, `bectl activate clean-install` and reboot returns
you to this exact state. Use it before each numbered phase, not only at the end.

---

## Phase 1 — first-boot baseline

### 1.1 One account, one privilege path

```sh
pw useradd -n admin -u 1001 -s /bin/sh -m -G wheel
passwd admin
```

From now on work as `admin` and prefix privileged commands with `doas`. Using
`su`/root logins daily hides which command needed privilege; doas logs every one
of them to syslog.

```sh
pkg bootstrap -y
pkg install -y doas
install -m 600 /dev/null /usr/local/etc/doas.conf
cat > /usr/local/etc/doas.conf <<'EOF'
permit persist :wheel
permit nopass :wheel cmd /usr/sbin/pkg args upgrade
EOF
```

`persist` keeps the doas timestamp for a few minutes inside one terminal, so a
phase of work does not ask six times. The second rule allows a fully unattended
`pkg upgrade`; remove it if you want a password on every package operation.

If `sudo` was installed, remove it now: two privilege paths means two things to
audit.

```sh
pkg delete -y sudo 2>/dev/null || true
```

Verify in a new login that `doas id` prints `uid=0` and that a plain user cannot
edit `/etc/pf.conf`.

### 1.2 Locale, keymap, time

```sh
locale -a | grep -i 'en_US.UTF-8'
sysrc keymap="pt.iso.acc"      # use the keymap your keyboard actually has
cat >> /etc/profile <<'EOF'
export LANG=en_US.UTF-8
export MM_CHARSET=UTF-8
EOF
```

Set the clock once, properly. A router with a wrong clock produces useless logs
and broken DNSSEC:

```sh
tzsetup
rm -f /etc/wall_cmos_clock          # RTC in UTC, the only sane default
```

### 1.3 Update the base before hardening it

```sh
freebsd-update fetch install
pkg update
pkg upgrade -y
```

### 1.4 CPU microcode

Intel microcode is a security control, not an optional extra: the MDS/VERW
mitigation below is meaningless without it.

```sh
pkg install -y cpu-microcode
sysrc microcode_update_enable=YES
```

If `cpu-microcode` is not in your repository, `pkg search microcode` and install
the Intel data package it names.

### 1.5 Checkpoint

```sh
bectl create phase1-done
reboot
```

After the reboot confirm `dmesg | grep -i microcode` reports an update and
`sysctl hw.ncpu` still shows 12 (SMT is switched off in the next phase).

---

## Phase 2 — firmware, loader, kernel hardening

### 2.1 Firmware settings (do these once, in the BIOS/UEFI)

| Setting | Value | Why |
| --- | --- | --- |
| VT-x / VMX | on | bhyve needs it |
| VT-d / IOMMU | on | required if a VM ever gets a passed-through device |
| Hyper-Threading | off if the firmware offers it | stronger than the kernel switch: the logical CPUs never appear |
| Intel iGPU | off | one GPU, one driver, less attack surface |
| Secure Boot | off | FreeBSD's loader is not signed for the Microsoft KEK |
| CSM / legacy boot | off | UEFI only |
| Boot order | internal disk only | no USB or network boot |
| USB boot | disabled | physical access is then worth less |
| Supervisor password | set | prevents the two settings above from being changed |
| Wake-on-LAN | off on both NICs | no remote power-on from the WAN |

Secure Boot being off is a gap, not a preference. Compensate with a firmware
password, a restricted boot order, and encrypted data (phase 4).

### 2.2 `/boot/loader.conf`

The loader is the only place some of these knobs exist, and loading modules here
rather than at runtime keeps them compatible with `securelevel=1` later.

```sh
cat > /boot/loader.conf <<'EOF'
autoboot_delay="3"
beastie_disable="YES"
console="vidconsole"

# SMT off: 12 threads become 6 CPUs
kern.smp.hyperthreading_allowed="0"
# accounting, required by rctl in phase 12
kern.racct.enable="1"

# ASLR and W^X
kern.elf64.aslr.enable="1"
kern.elf64.aslr.pie_enable="1"
kern.elf64.allow_wx="0"
kern.elf32.allow_wx="0"

# CPU mitigations (need the microcode from phase 1)
hw.mds_disable="1"
hw.ibrs_disable="0"

# ZFS: 6 GiB ARC out of 16 GiB
vfs.zfs.arc_max="6442450944"
vfs.zfs.vdev.trim_on_init="1"

# modules that must exist before securelevel is raised
nvidia-modeset_load="YES"
vmm_load="YES"
EOF
```

Notes that matter:

- `kern.smp.hyperthreading_allowed` is read at boot and read-only afterwards.
  If your kernel predates it, the older name is
  `machdep.hyperthreading_allowed=0`; if neither exists, disable HT in firmware.
- Load `linux_load="YES"` **here** if you ever want the Linuxulator. Its rc
  script loads the module at runtime, which `securelevel=1` forbids.
- `kern.elf64.allow_wx=0` breaks any program that maps memory writable and
executable at once. Firefox's JIT is the usual victim; Chromium is not. The
  surgical fix is per binary, not global:

```sh
elfctl -e +wxneeded /usr/local/lib/firefox/firefox
```

- `if_wg_load="YES"` belongs here only if you use the WireGuard section in
  phase 8.

### 2.3 Reboot and verify the kernel state

```sh
reboot
sysctl kern.smp.hyperthreading_allowed hw.ncpu
sysctl kern.elf64.allow_wx kern.elf64.aslr.enable
sysctl hw.mds_disable hw.ibrs_disable
kldstat -m nvidia-modeset
```

Expected: hyperthreading `0`, `hw.ncpu` 6, `allow_wx` 0, ASLR 1, `mds_disable`
1, and the NVIDIA module listed. If `hw.ncpu` is still 12, the firmware kept HT
and the tunable was not honoured — fix that before continuing, because every
capacity number later assumes 6 CPUs.

### 2.4 Checkpoint

```sh
bectl create phase2-done
```

---

## Phase 3 — sysctl hardening

One file, grouped by what each knob protects. Every line has a cost; the notes
below the block name them.

```sh
cat > /etc/sysctl.conf <<'EOF'
# --- kernel ---
kern.securelevel=1
kern.coredump=0
security.bsd.hardlink_check_uid=1
security.bsd.hardlink_check_gid=1
security.bsd.see_other_uids=0
security.bsd.see_other_gids=0
security.bsd.see_other_jails=0
security.bsd.unprivileged_proc_debug=0
security.bsd.unprivileged_read_msgbuf=0

# --- IPv4 stack ---
net.inet.ip.forwarding=1
net.inet.ip.redirect=0
net.inet.ip.sourceroute=0
net.inet.ip.accept_sourceroute=0
net.inet.ip.random_id=1
net.inet.icmp.drop_redirect=1
net.inet.icmp.log_redirect=0
net.inet.tcp.blackhole=2
net.inet.udp.blackhole=1
net.inet.tcp.syncookies=1

# --- IPv6: present but not routed, and not reachable ---
net.inet6.ip6.forwarding=0
net.inet6.ip6.redirect=0
net.inet6.icmp6.rediraccept=0

# --- bridge filtering for jails and VMs (phase 12) ---
net.link.bridge.pfil_bridge=1
net.link.bridge.pfil_member=0
net.link.bridge.pfil_onlyip=1
EOF
```

What each group does, and what it breaks:

| Knob | Effect | Cost |
| --- | --- | --- |
| `kern.securelevel=1` | no `kldload`, no writes to `/dev/mem`, no raw disk writes, immutable flags cannot be cleared | modules must be in `loader.conf`; no loading a driver "just to test" without a reboot |
| `kern.coredump=0` | crashes write no memory image to disk | no post-mortem of a userland crash; re-enable temporarily when debugging |
| `hardlink_check_*` | users cannot hardlink files they do not own (classic `/etc/shadow` trick) | none in normal use |
| `see_other_uids/gids` | `ps` shows only your processes | breaks multi-user debugging, does not affect root |
| `see_other_jails=0` | one jail cannot enumerate another's processes | jail tooling that expects host visibility must run as root |
| `unprivileged_proc_debug=0` | `ptrace` of another user's process is refused | `gdb`/`truss` on your own processes still works; crash reporters stop attaching |
| `unprivileged_read_msgbuf=0` | `dmesg` needs root | users lose `dmesg`; that buffer leaks pointers and device paths |
| `ip.forwarding=1` | the host routes | nothing; `gateway_enable=YES` in phase 5 sets it too |
| `ip.redirect=0`, `drop_redirect=1` | the host never acts as a redirector and ignores ICMP redirects | none on a single-homed-per-subnet router |
| `sourceroute` off | source-routed packets dropped | none |
| `random_id=1` | random IP IDs | none |
| `tcp.blackhole=2` | closed TCP ports get no RST at all | local client connections fail by timeout instead of immediately |
| `udp.blackhole=1` | closed UDP ports get no ICMP unreachable | same, for UDP-based discovery protocols |
| `syncookies=1` | SYN flood cannot exhaust the state table | none measurable |
| IPv6 block | no IPv6 path exists because pf only passes `inet` | anything that insists on IPv6 needs the appendix in phase 6 |

`securelevel=1` is the single most consequential line in this file. It is also
the reason phase 2 put every module in `loader.conf`: at securelevel 1,
`kldload` returns `EPERM`, and services that load modules at start (Linuxulator,
for example) fail silently enough to be confusing.

Apply and verify:

```sh
sysctl -f /etc/sysctl.conf
sysctl kern.securelevel security.bsd.unprivileged_proc_debug
sysctl net.inet.tcp.blackhole net.inet.udp.blackhole
```

Some read-only values only take effect at boot; reboot before believing the
output. `kern.securelevel` must read `1` after the reboot, and `kldload vmm`
must now fail — that failure is the feature.

### 3.1 Checkpoint

```sh
bectl create phase3-done
```

---

## Phase 4 — storage, swap, permissions

### 4.1 Dataset layout

The installer gives you `zroot/ROOT/default`. Split the rest so that snapshots,
quotas and mount options are per-purpose instead of all-or-nothing.

| Dataset | Mountpoint | Options |
| --- | --- | --- |
| `zroot/ROOT/default` | `/` | `atime=off`, `compression=lz4` |
| `zroot/home` | `/home` | `compression=zstd-3`, `setuid=off` |
| `zroot/var/log` | `/var/log` | `compression=zstd-9`, `exec=off` |
| `zroot/var/db` | `/var/db` | `exec=off`, `setuid=off` |
| `zroot/jails` | `/usr/local/jails` | `exec=off` on the parent, per-jail datasets inherit differently |
| `zroot/vm` | `/vm` | `recordsize=128k` |
| `zroot/backup` | `/backup` | local staging only, not a backup |

```sh
zfs create -o mountpoint=/home -o compression=zstd-3 -o setuid=off zroot/home
zfs create -o mountpoint=/var/log -o compression=zstd-9 -o exec=off zroot/var/log
zfs create -o mountpoint=/var/db -o exec=off -o setuid=off zroot/var/db
zfs create -o mountpoint=/usr/local/jails zroot/jails
zfs create -o mountpoint=/vm -o recordsize=128k zroot/vm
zfs create -o mountpoint=/backup zroot/backup
```

If `/home` already holds data, move it first; `zfs create` refuses a non-empty
mountpoint. `exec=off` on `/var/log` and `/var/db` is deliberate: nothing there
should ever be executed, and it removes a favourite drop location.

Pool-wide defaults:

```sh
zfs set atime=off zroot
zfs set compression=lz4 zroot
zpool set autotrim=on zroot
zpool set autoreplace=on zroot
```

`lz4` is the desktop choice: it is effectively free on an Intel core and it
shrinks kernel sources, packages and logs. `zstd-3` on `/home` buys more space
for files that already compress well, at a small CPU cost.

### 4.2 `/tmp` in memory

```sh
cat >> /etc/fstab <<'EOF'
tmpfs /tmp tmpfs rw,mode=1777,size=4g 0 0
EOF
```

4 GiB of the 16 GiB budget is enough for browser caches and build output, and
`/tmp` is emptied by every reboot. Do **not** put `/var/tmp` on tmpfs: package
builds and some installers expect it to survive.

### 4.3 Swap

If the installer created a swap **partition**, encrypt it with a random key at
every boot. Nothing readable is left on disk after power-off, and there is no
key to steal.

```sh
sysrc geli_swap_flags="-e AES-XTS -l 256 -s 4096 -d"
sysrc dumpdev="NO"
```

If swap is a **zvol** (`zroot/swap`), the same line still applies to the zvol
device; verify with `swapinfo -h` after the reboot. If your swap is a file,
replace it with a partition or zvol before continuing — encrypted swap is not
optional on a laptop-shaped threat model.

`dumpdev="NO"` follows from the random key: kernel crash dumps would be written
to a device whose key is destroyed at reboot, so they would be unreadable
garbage. If kernel debugging matters more than swap confidentiality on this
machine, drop both lines.

### 4.4 File modes

```sh
chmod 700 /root
chmod 600 /usr/local/etc/doas.conf
chmod 600 /etc/ssh/sshd_config
chmod 700 /var/crash 2>/dev/null || true
```

`/etc/ssh/sshd_config` is 600 by default in recent FreeBSD; setting it again
costs nothing and catches a sloppy restore from a backup.

### 4.5 Verify

```sh
zfs list -o name,mountpoint,compression,atime,exec,setuid
swapinfo -h
mount | grep ' /tmp '
```

---

## Phase 5 — network layout

Two physical NICs, two internal bridges with no physical member. The LAN is
routed, not bridged: the host is the only path between LAN, WAN, jails and VMs.
That is what makes a single pf ruleset meaningful.

```sh
ifconfig -l
pciconf -lv | grep -B3 -A2 network
```

Confirm which name is the WAN (the one with the cable to the modem) before you
write a single rule. The rest of the document assumes `em0` = WAN,
`igc0` = LAN.

### 5.1 `/etc/rc.conf` network block

```sh
cat >> /etc/rc.conf <<'EOF'
hostname="gw.lan.example"
ifconfig_em0="DHCP"
ifconfig_igc0="inet 10.20.0.1 netmask 255.255.255.0"
gateway_enable="YES"
ipv6_activate_all_interfaces="NO"
cloned_interfaces="bridge1 vmnet"
ifconfig_bridge1="inet 10.30.0.1/24 up"
ifconfig_vmnet="inet 10.40.0.1/24 up"
EOF
```

- `bridge1` and `vmnet` start with no members. Jails and VMs attach to them
  later; nothing on the LAN can reach those subnets at layer 2.
- `gateway_enable=YES` sets `net.inet.ip.forwarding=1` at boot; phase 3 already
  set it in `sysctl.conf`, which is harmless duplication.
- If the ISP needs PPPoE, `em0` gets no address and `mpd5` owns the WAN instead.
  That is a separate configuration; do not mix it with `DHCP`.

DNS resolution for the host itself points at the local resolver built in
phase 7:

```sh
cat > /etc/resolv.conf <<'EOF'
nameserver 127.0.0.1
EOF
```

### 5.2 Apply and verify

```sh
service netif restart
service routing restart
ifconfig -l
ifconfig em0 | grep 'inet '
ifconfig igc0 | grep 'inet '
netstat -rn -f inet
```

Expected: a DHCP address on `em0`, `10.20.0.1` on `igc0`, and a default route
through `em0`. `bridge1` and `vmnet` exist and answer nothing yet.

Test forwarding before pf exists:

```sh
sysctl net.inet.ip.forwarding
nc -vz 1.1.1.1 443
```

A client on the LAN is not configured yet, so the only proof available here is
that the host itself routes. The real forwarding test comes after pf in the next
phase.

---

## Phase 6 — pf: default deny, NAT, and one published jail

### 6.1 The ruleset

Read the ordering before copying it. pf keeps the **last** matching rule unless a
rule says `quick`, so the `block` lines at the top are the default, and each
`pass` below them overrides it for one narrow case. The `quick` rules are the
exceptions that must not fall through to a later, wider pass.

```sh
cat > /etc/pf.conf <<'EOF'
# interfaces
ext_if  = "em0"
lan_if  = "igc0"
jail_if = "bridge1"
vm_if   = "vmnet"

# networks
lan_net  = "10.20.0.0/24"
jail_net = "10.30.0.0/24"
vm_net   = "10.40.0.0/24"

# host addresses
gw_lan  = "10.20.0.1"
gw_jail = "10.30.0.1"
gw_vm   = "10.40.0.1"

# the only service published to the internet
web_jail = "10.30.0.10"

set skip on lo0
set block-policy drop
set loginterface $ext_if
set limit { states 100000, src-nodes 20000, frags 5000, table-entries 200000 }
set optimization normal
set timeout { tcp.established 86400, tcp.closing 300, udp.first 60, \
              udp.single 30, udp.multiple 60, icmp.first 20, icmp.error 10, \
              other.first 60 }

scrub in all fragment reassemble

table <bruteforce> persist
table <martians> persist { 0.0.0.0/8, 127.0.0.0/8, 169.254.0.0/16, \
    172.16.0.0/12, 192.0.0.0/24, 192.0.2.0/24, 192.168.0.0/16, \
    198.18.0.0/15, 198.51.100.0/24, 203.0.113.0/24, 240.0.0.0/4 }

antispoof quick for lo0
antispoof quick for $lan_if
antispoof quick for $ext_if
block in quick on $ext_if from <martians> to any
block in quick on $ext_if from <bruteforce> to any
anchor "blacklistd/*" in on $ext_if

# default deny
block in log all
block out log all

# host outbound
pass out quick inet keep state

# --- WAN ---
pass in on $ext_if inet proto icmp icmp-type { echoreq, unreach } keep state
rdr pass on $ext_if inet proto tcp to port { http, https } -> $web_jail

# --- LAN to the gateway itself: ssh, dns, icmp, nothing else ---
pass in quick on $lan_if inet proto tcp from $lan_net to $gw_lan port ssh \
    keep state (max-src-conn 10, max-src-conn-rate 5/60, \
                overload <bruteforce> flush global)
pass in quick on $lan_if inet proto { tcp, udp } from $lan_net to $gw_lan port domain keep state
pass in quick on $lan_if inet proto icmp from $lan_net to $gw_lan icmp-type echoreq keep state
block in quick on $lan_if from $lan_net to $gw_lan

# --- DHCP broadcast from clients ---
pass in quick on $lan_if inet proto udp from any to 255.255.255.255 port bootps keep state

# --- LAN to published jail services only ---
pass in quick on $lan_if inet proto tcp from $lan_net to $jail_net port { http, https } keep state
block in quick on $lan_if from $lan_net to { $jail_net, $vm_net }

# --- LAN to the internet ---
pass in on $lan_if from $lan_net to ! $gw_lan keep state

# --- jails ---
pass in quick on $jail_if inet proto { tcp, udp } from $jail_net to $gw_jail port domain keep state
block in quick on $jail_if from $jail_net to { $gw_lan, $gw_jail, $gw_vm }
block in quick on $jail_if from $jail_net to { $lan_net, $vm_net, $jail_net }
pass in on $jail_if from $jail_net to any keep state

# --- VMs ---
pass in quick on $vm_if inet proto { tcp, udp } from $vm_net to $gw_vm port domain keep state
block in quick on $vm_if from $vm_net to { $gw_lan, $gw_jail, $gw_vm }
block in quick on $vm_if from $vm_net to { $lan_net, $jail_net, $vm_net }
pass in on $vm_if from $vm_net to any keep state

# --- NAT ---
nat on $ext_if inet from { $lan_net, $jail_net, $vm_net } to any -> ($ext_if)
EOF
```

The four decisions worth defending:

1. **Jails cannot reach the LAN or each other.** They reach DNS on the gateway
   and the internet through NAT. A compromised web jail has no path to a client
   laptop and no path to a database jail. If two jails must talk, add an
   explicit pair of `pass` rules with the exact addresses and ports; never
   remove the blanket block.
2. **The gateway answers only ssh, dns and ping on the LAN.** No web UI, no
   `pkg` proxy, nothing else on 10.20.0.1.
3. **One inbound service.** `rdr pass` maps WAN 80/443 to `web_jail`; every other
   inbound port dies at `block in`. There is no SSH on the WAN interface at all.
4. **NAT is a side effect, not the firewall.** The `pass` rules decide what may
   traverse; `nat` only rewrites the source. Removing NAT would leave the
   filtering identical.

### 6.2 Enable pf and the log interface

```sh
sysrc pf_enable=YES
sysrc pf_rules=/etc/pf.conf
sysrc pflog_enable=YES
sysrc pflog_logfile=/var/log/pflog
pfctl -nf /etc/pf.conf          # syntax check, changes nothing
service pf start
pfctl -sr | head -20
```

`pfctl -nf` must print nothing. If it complains, fix the file before starting
pf; a half-applied ruleset on a router is how networks go dark.

### 6.3 Test matrix

Do these in order, with a console attached. Each line is a pass/fail you can see.

| From | Action | Expected |
| --- | --- | --- |
| LAN client | `ping 10.20.0.1` | replies |
| LAN client | `drill @10.20.0.1 freebsd.org` | resolves (after phase 7) |
| LAN client | `ssh admin@10.20.0.1` | connects |
| LAN client | `nc -vz 10.20.0.1 22` and `443` | 22 open, 443 closed |
| LAN client | `ping 1.1.1.1` | replies through NAT |
| LAN client | `nc -vz 10.30.0.10 80` | open only if the jail is up |
| WAN | external scan of ports 22/80/443 | 22 filtered, 80/443 to the jail |
| jail | `ping 10.20.0.10` | blocked |
| jail | `nc -vz 10.30.0.11 3306` | blocked |
| jail | `drill @10.30.0.1 freebsd.org` | resolves |
| host | `pfctl -si \| grep -E 'State|Counters'` | states growing, no drops you cannot explain |

Watch the decisions live while testing:

```sh
tcpdump -ni pflog0 -e -ttt
pfctl -t bruteforce -T show
pfctl -ss | wc -l
```

### 6.4 The lockout drill

Before you rely on this, break it on purpose once: from a LAN client, run
`ssh admin@10.20.0.1 'doas pfctl -d'` and confirm you can still reach the host,
then `doas pfctl -f /etc/pf.conf` from the console to restore. You now know both
directions of the escape hatch, which is worth more than a perfect first copy of
the ruleset.

### 6.5 Checkpoint

```sh
bectl create phase6-done
```

---

## Phase 7 — resolver, DHCP, time

### 7.1 Recursive resolver with DNSSEC

FreeBSD ships `local_unbound` in the base system: a validating, recursive
resolver with no third-party forwarder in the path. That is the OpenBSD-style
choice — the machine answers from the root, so the ISP cannot see or rewrite
individual queries.

```sh
cat > /var/unbound/unbound.conf <<'EOF'
server:
    interface: 127.0.0.1
    interface: 10.20.0.1
    interface: 10.30.0.1
    interface: 10.40.0.1
    access-control: 127.0.0.0/8 allow
    access-control: 10.20.0.0/24 allow
    access-control: 10.30.0.0/24 allow
    access-control: 10.40.0.0/24 allow

    do-ip4: yes
    do-ip6: no
    do-udp: yes
    do-tcp: yes

    root-hints: "/var/unbound/root.hints"
    auto-trust-anchor-file: "/var/unbound/root.key"

    hide-identity: yes
    hide-version: yes
    harden-glue: yes
    harden-dnssec-stripped: yes
    harden-below-nxdomain: yes
    harden-referral-path: yes
    harden-algo-downgrade: yes
    qname-minimisation: yes
    aggressive-nsec: yes
    use-caps-for-id: yes
    rrset-roundrobin: yes
    minimal-responses: yes
    prefetch: yes

    cache-min-ttl: 300
    cache-max-ttl: 86400
    serve-expired: yes
    msg-cache-size: 64m
    rrset-cache-size: 128m
    key-cache-size: 32m
    neg-cache-size: 8m
    num-threads: 2
    so-reuseport: yes

    private-address: 10.20.0.0/24
    private-address: 10.30.0.0/24
    private-address: 10.40.0.0/24
    private-address: 169.254.0.0/16
    private-address: 172.16.0.0/12
    private-address: 192.168.0.0/16

remote-control:
    control-enable: yes
    control-interface: /var/run/local_unbound.ctl
EOF
```

- `interface:` lines are the only places the resolver listens. No listener on
  the WAN address, so pf is not the only thing keeping it private.
- `private-address` is rebind protection: a public answer pointing at RFC1918
  space is discarded. It also means you cannot publish `10.x` names from the
  public DNS — correct for this network.
- `num-threads: 2` is right for six CPUs and a residential query load; more
  threads only add cache contention.

```sh
sysrc local_unbound_enable=YES
unbound-checkconf /var/unbound/unbound.conf
service local_unbound start
drill @127.0.0.1 freebsd.org
drill @127.0.0.1 dnssec-failed.org
```

The second query must return `SERVFAIL`: that is DNSSEC validation actually
working. If it resolves, you are forwarding to a resolver that does not
validate, and the whole section bought you nothing.

### 7.2 The pf gap this creates

pf currently lets LAN clients reach only ssh, dns and icmp on the gateway.
DHCP option 42 below hands out `10.20.0.1` as the time server, so add one line
next to the DNS rule in `/etc/pf.conf`:

```
pass in quick on $lan_if inet proto udp from $lan_net to $gw_lan port ntp keep state
```

Then reload, always with a syntax check first:

```sh
pfctl -nf /etc/pf.conf && pfctl -f /etc/pf.conf
```

This is the normal shape of a default-deny router: every new service is a new
hole, added on purpose, in one place.

### 7.3 DHCP with Kea

The base system has no DHCP server. Kea is the current ISC server and the one
the ports tree maintains; `dnsmasq` is a smaller alternative if you prefer one
binary for DNS and DHCP, at the cost of giving up a dedicated validator.

```sh
pkg install -y kea
install -d -m 750 /var/db/kea
install -m 640 /dev/null /var/log/kea-dhcp4.log
```

`/usr/local/etc/kea/kea-dhcp4.conf`:

```json
{
  "Dhcp4": {
    "interfaces-config": {
      "interfaces": [ "igc0" ],
      "dhcp-socket-type": "udp"
    },
    "control-socket": {
      "socket-type": "unix",
      "socket-name": "/var/run/kea/kea4-ctrl-socket"
    },
    "lease-database": {
      "type": "memfile",
      "persist": true,
      "name": "/var/db/kea/kea-leases4.csv",
      "lfc-interval": 3600
    },
    "authoritative": true,
    "valid-lifetime": 3600,
    "renew-timer": 900,
    "rebind-timer": 1800,
    "subnet4": [
      {
        "id": 1,
        "subnet": "10.20.0.0/24",
        "pools": [ { "pool": "10.20.0.100 - 10.20.0.200" } ],
        "option-data": [
          { "name": "routers", "data": "10.20.0.1" },
          { "name": "domain-name-servers", "data": "10.20.0.1" },
          { "name": "domain-name", "data": "lan.example" },
          { "name": "ntp-servers", "data": "10.20.0.1" }
        ]
      }
    ],
    "loggers": [
      {
        "name": "kea-dhcp4",
        "output_options": [
          { "output": "/var/log/kea-dhcp4.log", "flush": true }
        ],
        "severity": "INFO"
      }
    ]
  }
}
```

```sh
kea-dhcp4 -t /usr/local/etc/kea/kea-dhcp4.conf
sysrc kea_dhcp4_enable=YES
service kea start
sockstat -4l | grep ':67'
```

If clients get no lease, the two usual causes are the socket type (try
`"raw"`) and pf dropping the broadcast — the `bootps` rule in phase 6 is the
one that must exist. Check with `tcpdump -ni igc0 port 67 or port 68`.

### 7.4 Time

Every log line and every DNSSEC signature depends on the clock.

```sh
cat > /etc/ntp.conf <<'EOF'
pool 2.freebsd.pool.ntp.org iburst

restrict default limited kod nomodify notrap nopeer noquery
restrict 127.0.0.1
restrict ::1
restrict 10.20.0.0 mask 255.255.255.0 nomodify notrap nopeer
restrict 10.30.0.0 mask 255.255.255.0 nomodify notrap nopeer
restrict 10.40.0.0 mask 255.255.255.0 nomodify notrap nopeer

leapfile "/var/db/ntpd.leap-seconds.list"
EOF

sysrc ntpd_enable=YES
sysrc ntpd_sync_on_start=YES
service ntpd start
ntpq -p
```

`nomodify notrap nopeer` means clients may ask the time and nothing else;
`noquery` is absent from the LAN lines on purpose, because those clients are
the ones querying.

---

## Phase 8 — sshd

SSH is the only administrative path, and it exists on the LAN address only.

```sh
ls -l /etc/ssh/ssh_host_ed25519_key || \
  ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key -N ''
```

`/etc/ssh/sshd_config`:

```
Port 22
AddressFamily inet
ListenAddress 10.20.0.1

HostKey /etc/ssh/ssh_host_ed25519_key

PermitRootLogin no
PubkeyAuthentication yes
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitEmptyPasswords no
AuthenticationMethods publickey

AllowUsers admin
MaxAuthTries 3
MaxSessions 4
LoginGraceTime 20
ClientAliveInterval 300
ClientAliveCountMax 2

AllowAgentForwarding no
AllowTcpForwarding no
X11Forwarding no
PermitTunnel no
GatewayPorts no
PermitUserEnvironment no
UseDNS no
LogLevel VERBOSE

KexAlgorithms sntrup761x25519-sha512@openssh.com,curve25519-sha256,curve25519-sha256@libssh.org,diffie-hellman-group16-sha512
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com
```

Why each line that looks redundant is not:

- `ListenAddress 10.20.0.1` is the actual control that keeps SSH off the WAN.
  It also means `ssh` from a jail is impossible even if pf were wrong.
- `AuthenticationMethods publickey` makes a second factor mandatory in the
  config, not by convention. `PasswordAuthentication no` is belt and braces.
- `UseDNS no` removes a resolver round-trip from every login and a data leak to
  the resolver.
- `AllowUsers admin` fails closed if a package creates a service account with a
  shell.
- Forwarding and tunnels are off: a stolen key should copy files, not become a
  pivot into the LAN.

Install your public key before restarting, or you will lock yourself out:

```sh
install -d -m 700 -o admin -g admin /home/admin/.ssh
install -m 600 -o admin -g admin /dev/null /home/admin/.ssh/authorized_keys
# paste the contents of your laptop's id_ed25519.pub into that file
```

```sh
sshd -t
sysrc sshd_enable=YES
service sshd restart
```

Test both directions from a LAN client:

```sh
ssh admin@10.20.0.1 true                                  # must work
ssh -o PubkeyAuthentication=no -o PreferredAuthentications=password admin@10.20.0.1 true
                                                          # must be refused
```

### 8.1 Remote access, if you ever need it

There is deliberately no WAN SSH rule. If you need access from outside, use
WireGuard (`pkg install wireguard-tools`, `if_wg` loaded from `loader.conf`),
and remember that pf will not load a rule naming `wg0` until that interface
exists. Bring the tunnel up first, add
`pass in on wg0 from 10.99.0.0/24 to any keep state` plus a UDP 51820 rule,
check with `pfctl -nf`, then reload. Do it with a console attached, once,
before you depend on it.

### 8.2 Checkpoint

```sh
bectl create phase8-done
```

---

## Phase 9 — remove services, then constrain what is left

### 9.1 Turn off what this machine does not do

```sh
sysrc sendmail_enable=NONE
sysrc sendmail_submit_enable=NO
sysrc sendmail_outbound_enable=NO
sysrc sendmail_msp_queue_enable=NO
sysrc syslogd_flags="-ss"
sysrc inetd_enable=NO
sysrc rpcbind_enable=NO
sysrc rwhod_enable=NO
sysrc nfs_server_enable=NO
```

`syslogd_flags="-ss"` means: do not listen on the network at all, and do not
resolve hostnames in log lines. Both remove a parser and a resolver call from
the log path.

Audit what is still listening before adding anything:

```sh
service -e
sockstat -4 -l
sockstat -6 -l
```

Expected on the LAN: `sshd` on 10.20.0.1:22, `unbound` on 53 and `kea` on 67.
Anything else is a decision you have not made yet.

### 9.2 Raw disks for root only

```sh
cat > /etc/devfs.rules <<'EOF'
[system=10]
add path 'ada*' mode 0640 group operator
add path 'da*' mode 0640 group operator
add path 'nvd*' mode 0640 group operator
add path 'zvol/*' mode 0640 group operator
EOF
sysrc devfs_system_ruleset=system
# the rule set is applied at the next boot; do not stop devfs to apply it
```

Do not add anyone to `operator`. The group exists so that a backup tool can be
given read access deliberately; by default the set is empty.

### 9.3 The security framework: TrustedBSD MAC

The thing you heard about is the **TrustedBSD MAC framework**: pluggable,
 kernel-enforced access policies that sit beside the Unix permission model.
It is not one setting; it is a set of modules, each answering a different
question. On a desktop-and-router the three useful ones are:

| Module | Question it answers | Effect here |
| --- | --- | --- |
| `mac_seeotheruids` | may a user see another user's processes? | same as `security.bsd.see_other_uids=0`, enforced by the module |
| `mac_bsdextended` | may this uid touch that uid's files at all? | a second, uid-based layer over file mode bits (`ugidfw`) |
| `mac_portacl` | may this uid bind this port? | lets a service run unprivileged and still bind 80/443 |

`mac_mls` and `mac_biba` (labels, compartments) exist and are the "real" MAC,
but they require labelling every file on the system. On a single-user desktop
they add mislabelling bugs, not safety. Do not enable them.

Modules must be loaded at boot, because phase 3 raised the securelevel:

```sh
cat >> /boot/loader.conf <<'EOF'
mac_seeotheruids_load="YES"
mac_bsdextended_load="YES"
mac_portacl_load="YES"
EOF
```

`mac_bsdextended` is only useful with rules; `ugidfw` is in the base system:

```sh
ugidfw list
```

An empty list is the correct starting point. A defensible first rule denies the
browser account (if you create one) any access to root-owned files:

```sh
ugidfw add subject uid 1002 object uid 0 mode n
ugidfw list
```

Rules are evaluated in order and can break a login if written carelessly. Test
with a second session already open, and remove with `ugidfw delete <rule>`
(the number shown by `ugidfw list`). `mac_portacl` is set with
`security.mac.portacl.rules` and is only worth it if you later run a service as
a non-root uid; leave it unconfigured until then:

```
security.mac.portacl.port_high=1023
security.mac.portacl.suser_exempt=1
```

### 9.4 Capsicum: the sandbox inside normal programs

Capsicum is FreeBSD's capability mode (`cap_enter(2)`): a process gives up the
right to open new paths or sockets, keeping only the descriptors it already
holds. You do not configure it — programs opt in. Chromium's renderer, `dhclient`,
`tcpdump` and parts of `sshd` already do, which is why the browser section below
matters more than any browser flag.

The controls on your side are the ones already applied: `unprivileged_proc_debug=0`,
`allow_wx=0`, ASLR, and not running anything as root that does not need it.

### 9.5 Sandboxing is a stack, not a checkbox

| What you run | Isolation |
| --- | --- |
| Chromium renderers | Capsicum sandbox, one process per site |
| Services (web, database, anything network-facing) | vnet jail, phase 12 |
| Untrusted binaries, other operating systems | bhyve VM, phase 13 |
| One-off suspicious file | `bhyve` guest, or a jail with no network |
| Everything else on the desktop | normal user, no root, MAC and W^X as backstop |

There is no `firejail` on FreeBSD and you should not look for one: the kernel
already provides the primitives, and a jail or a VM is stronger than a
seccomp-style filter bolted onto a desktop app.

---

## Phase 10 — NVIDIA, X11, i3

### 10.1 Driver

```sh
pkg install -y nvidia-driver nvidia-settings
pkg install -y xorg i3 i3status dmenu xterm chromium
pkg install -y dejavu xorg-fonts-truetype
```

Check the card was recognised before blaming the driver:

```sh
pciconf -lv | grep -A4 vgapci
kldstat -m nvidia-modeset
nvidia-smi
```

`nvidia-smi` printing the card, driver version and memory is the proof that the
kernel module, the userland library and the device node all agree. If it fails,
the order to check is: module loaded from `loader.conf`, GPU in the supported
list of the installed driver version (`pkg info -D nvidia-driver`), and the
iGPU disabled in firmware.

Do not install `drm-kmod` or `i915kms` on this machine. One GPU, one driver.
The `nvidia-drm-kmod` port exists only for Wayland; this build is X11.

### 10.2 `/usr/local/etc/X11/xorg.conf.d/20-nvidia.conf`

```ini
Section "Device"
    Identifier  "NVIDIA0"
    Driver      "nvidia"
    BusID       "PCI:1:0:0"
    Option      "NoLogo" "true"
    Option      "AllowIndirectGLX" "off"
EndSection

Section "Screen"
    Identifier  "Screen0"
    Device      "NVIDIA0"
    DefaultDepth 24
    Option      "metamodes" "nvidia-auto-select +0+0"
    Option      "ForceFullCompositionPipeline" "on"
    SubSection "Display"
        Depth   24
        Modes   "1920x1080"
    EndSubSection
EndSection
```

`BusID` must match `pciconf -lv`: `pci0:1:0:0` becomes `PCI:1:0:0`, not `PCI:0:1:0`.
If the display stays black, remove the file, run `Xorg -configure`, and compare
what it detected with this one — do not guess the BusID.

`ForceFullCompositionPipeline` is the anti-tearing setting that works with a
non-compositing window manager like i3. If you later run a compositor, turn it
off again; the two together cost frames.

### 10.3 Keyboard layout for X

```ini
Section "InputClass"
    Identifier      "system-keyboard"
    MatchIsKeyboard "on"
    Option          "XkbLayout" "pt"
EndSection
```

Save as `/usr/local/etc/X11/xorg.conf.d/00-keyboard.conf`. This is separate
from the console keymap in phase 1; X does not read `rc.conf`.

### 10.4 i3, xterm, Chromium

```sh
sysrc dbus_enable=YES
sysrc moused_enable=YES        # only for a PS/2 mouse
```

`/home/admin/.xinitrc`:

```sh
exec i3
```

`/home/admin/.config/i3/config` — the smallest config that is actually usable:

```
set $mod Mod4
font pango:DejaVu Sans Mono 9

exec_always --no-startup-id xsetroot -solid "#101014"

bindsym $mod+Return exec xterm
bindsym $mod+d exec dmenu_run
bindsym $mod+Shift+q kill
bindsym $mod+Shift+r restart
bindsym $mod+Shift+e exec i3-msg exit

bar {
    status_command i3status
}
```

Start with `startx` from the console. A display manager is deliberately absent:
it is another root service, another parser and another login path for no gain on
a single-user workstation.

### 10.5 Chromium, sandboxed

```sh
chromium
```

Then check `chrome://sandbox`. It must report the sandbox as active and the
renderer processes in capability mode. Three rules that must not be broken:

1. Never start Chromium as root and never pass `--no-sandbox`. The second
   disables the only per-tab boundary the browser has.
2. Do not add `--disable-features` wholesale; each flag you paste from a forum
   is a subsystem switched off.
3. If Chromium crashes immediately after phase 3, the cause is almost always
   `security.bsd.unprivileged_proc_debug=0` or W^X on a JIT page. Test by
   raising one knob at a time, and if a binary genuinely needs WX, mark that
   one binary with `elfctl -e +wxneeded` rather than reverting the kernel.

Graphics check:

```sh
pkg install -y mesa-demos
glxinfo | grep -E 'OpenGL renderer|OpenGL version'
```

The renderer string must name the NVIDIA card. If it says `llvmpipe`, X is
running software rendering and the driver configuration above was not used.

### 10.6 Checkpoint

```sh
bectl create phase10-done
```

---

## Phase 11 — performance, with the numbers this machine has

16 GiB and six usable CPUs after SMT is off. That budget is spent as follows,
and none of it is folklore:

| Consumer | Budget | Where it is set |
| --- | --- | --- |
| ZFS ARC | 6 GiB | `vfs.zfs.arc_max` in `loader.conf` |
| OS, i3, X, services | ~1.5 GiB | — |
| Chromium with a handful of tabs | 2–4 GiB | runtime |
| one jail | 2 GiB cap | `rctl` in phase 12 |
| one VM | 4 GiB | bhyve config |
| headroom | the rest | — |

Do not raise the ARC to "use all the RAM". The point of the cap is that the
desktop never waits for ZFS to shrink the cache under memory pressure.

### 11.1 CPU frequency and idle states

```sh
sysrc powerd_enable=YES
sysrc powerd_flags="-a hiadaptive"
sysrc performance_cx_lowest="Cmax"
service powerd start
```

`hiadaptive` ramps aggressively on load and backs off when idle — the right
profile for a desktop that is also a router. `Cmax` keeps the cores out of deep
C-states, which removes wake-up latency at a small idle-power cost. On a
machine that runs 24/7 as a gateway, that trade is worth stating explicitly:
if electricity matters more than input latency, use `C2` instead.

Verify the governor is actually moving:

```sh
sysctl dev.cpu.0.freq dev.cpu.0.freq_levels
sysctl dev.cpu.0.cx_usage
```

### 11.2 What SMT cost you

With `kern.smp.hyperthreading_allowed=0`, `hw.ncpu` is 6 and every parallel job
is bounded by that. Expect roughly 20–30% less throughput on fully parallel
workloads (builds, compression, VM vCPU oversubscription) than the same CPU
with SMT on, and almost no difference in the single-threaded work a desktop
does. Size `-j` accordingly:

```sh
sysctl -n hw.ncpu          # 6, use this for make -j and VM vCPU counts
```

Do not "recover" the threads by overcommitting jails and VMs; six vCPUs total
across all guests is the honest limit.

### 11.3 Measure before and after

Every change in this document that claims a performance effect should be
checked here. There is no other way to know.

```sh
pkg install -y hyperfine

# disk
zpool iostat -v 1 5
gstat -p 1

# memory and ARC
sysctl vfs.zfs.arc_max
arcstat 1 5 2>/dev/null || kstat -p zfs:0:arcstats:size

# CPU and interrupts
vmstat -i | head
top -H -b -n 1 | head -15

# one repeatable job
hyperfine --warmup 2 'find /usr/src -name "*.c" | wc -l'
```

Change one line, rerun the same command, keep the change only if the number
moved in the direction you expected. `zfs set` and `sysctl -w` are reversible in
seconds; keep a note of the before value next to the change.

### 11.4 Things not to do

- **No `vfs.zfs.prefetch_disable` tweaks.** The default is correct for a
  desktop; disabling prefetch trades a benchmark for real latency.
- **No dedup.** It needs gigabytes of RAM to save a few percent on a
  single-user pool.
- **No `kern.ipc` or `net.inet.tcp` send/receive buffer inflation.** On a
  residential line the bottleneck is the line, and oversized buffers add
  latency for every client behind NAT.
- **No swap tuning.** Encrypted swap on a desktop is a safety net, not a
  performance tier; 4–8 GiB is enough to avoid the OOM killer on a bad day.

---

## Phase 12 — jails as the service sandbox

### 12.1 The design

One jail per service, each with its own vnet stack on `bridge1`, its own ZFS
dataset, no mount rights, `securelevel=2`, and an rctl memory cap. The host
never shares a filesystem with a jail, and pf already blocks jail→LAN,
jail→jail and jail→host-services in phase 6.

| Layer | Setting |
| --- | --- |
| network | vnet + `epair`, no host stack sharing |
| filesystem | separate dataset, `allow.mount=0` |
| kernel | `securelevel=2`, `children.max=0`, `enforce_statfs=2` |
| resources | `rctl` memory/CPU/process caps |
| packets | pf rules on `bridge1` |

### 12.2 Base and template

```sh
mkdir -p /usr/local/jails
zfs create -o mountpoint=/usr/local/jails/base zroot/jails/base
bsdinstall jail /usr/local/jails/base
zfs snapshot zroot/jails/base@clean
```

`bsdinstall jail` installs a minimal FreeBSD base into that directory using the
same release as the host. The snapshot is the template every jail clones from,
so a jail starts from a known-clean userland every time.

```sh
zfs clone -o mountpoint=/usr/local/jails/web zroot/jails/base@clean zroot/jails/web
```

### 12.3 `/etc/jail.conf`

```
exec.start  = "/bin/sh /etc/rc";
exec.stop   = "/bin/sh /etc/rc.shutdown";
exec.clean;
mount.devfs;
host.domainname = "lan.example";
path = "/usr/local/jails/$name";
persist;

web {
    vnet;
    vnet.interface = "epair0b";
    exec.prestart = "ifconfig epair0 create; ifconfig epair0a up; ifconfig bridge1 addm epair0a up";
    exec.poststop = "ifconfig bridge1 deletem epair0a; ifconfig epair0a destroy";

    allow.raw_sockets = 0;
    allow.sysvipc = 0;
    allow.mount = 0;
    allow.chflags = 0;
    allow.quotas = 0;
    allow.socket_af = 0;
    allow.mlock = 0;
    children.max = 0;
    enforce_statfs = 2;
    securelevel = 2;
    devfs_ruleset = 4;
}
```

Every `allow.*` above is a capability the jail does **not** get. `allow.mount=0`
is what stops a jailed root from mounting the host's datasets; `children.max=0`
stops nested jails; `devfs_ruleset=4` is the base system's jail device ruleset,
not the host's.

### 12.4 The jail's own configuration

```sh
cat > /usr/local/jails/web/etc/rc.conf <<'EOF'
hostname="web.lan.example"
ifconfig_epair0b="inet 10.30.0.10/24"
defaultrouter="10.30.0.1"
sshd_enable="NO"
sendmail_enable="NONE"
cron_enable="NO"
syslogd_flags="-ss"
ntpd_enable="NO"
EOF

cat > /usr/local/jails/web/etc/resolv.conf <<'EOF'
nameserver 10.30.0.1
EOF
```

No sshd inside a jail: administration goes through `jexec`, which requires root
on the host. That removes an entire authentication surface from every jail.

### 12.5 Start, cap, verify

```sh
sysrc jail_enable=YES
sysrc jail_list="web"
sysrc rctl_enable=YES

cat > /etc/rctl.conf <<'EOF'
jail:web:memoryuse:deny=2G
jail:web:vmemoryuse:deny=3G
jail:web:pcpu:deny=200
jail:web:maxproc:deny=200
EOF

service jail start web
service rctl start
```

`pcpu=200` is two full CPUs out of six. `memoryuse=2G` is a hard cap; the jail
is killed rather than allowed to starve the desktop.

```sh
jls
jexec web sh -c 'ifconfig; netstat -rn -f inet; drill @10.30.0.1 freebsd.org'
jexec web nc -vz 10.20.0.10 22        # must fail
rctl -h jail:web
```

The pf test from phase 6 is now real: the jail can resolve, reach the internet
through NAT, and cannot touch the LAN or the host's SSH.

### 12.6 Managing software inside the jail

```sh
pkg -j web bootstrap -y
pkg -j web install -y nginx
jexec web sysrc nginx_enable=YES
service jail restart web
```

`pkg -j` runs the package manager inside the jail's own root, so the host's
package database is never modified by a jailed service.

If you would rather not hand-maintain `jail.conf`, the ecosystem tools are
`bastille` (templates and `bastille pkg`), `pot` (lightweight jail manager) and
`cbsd`. They generate the same settings above; use one only after you can read
what it generated.

### 12.7 Checkpoint

```sh
bectl create phase12-done
```

---

## Phase 13 — bhyve for whole-OS isolation

### 13.1 `vmm(4)` is not only an OpenBSD thing

The name is the same on both systems and the code is not. On **OpenBSD**,
`vmm(4)` is the hypervisor behind `vmctl`. On **FreeBSD**, `vmm(4)` is the kernel
driver that `bhyve(8)` uses to run guests; you load it with `vmm_load="YES"`,
which phase 2 already did. There is no `vmctl` here and no OpenBSD code
involved. If a guide tells you to run `vmctl` on FreeBSD, it is the wrong guide.

```sh
kldstat -m vmm
sysctl -a | grep -i vmm | head
```

### 13.2 vm-bhyve

```sh
pkg install -y vm-bhyve
sysrc vm_enable=YES
sysrc vm_dir="zfs:zroot/vm"
vm init
```

`vm init` copies the template set into `/vm`. The switch is manual because
the guest network must be `vmnet`, the internal bridge from phase 5, never
the LAN:

```sh
vm switch create -t manual vmnet
vm switch list
ifconfig vmnet                # must show no member ports
```

### 13.3 One guest

```sh
vm iso https://download.freebsd.org/releases/amd64/amd64/ISO-IMAGES/15.0/FreeBSD-15.0-RELEASE-amd64-disc1.iso
```

`/vm/guest/guest.conf`:

```
guest="freebsd"
loader="uefi"
cpu=2
memory="4G"

network0_type="virtio-net"
network0_switch="vmnet"

disk0_type="virtio-blk"
disk0_name="disk0.img"
```

```sh
vm install guest FreeBSD-15.0-RELEASE-amd64-disc1.iso
vm console guest
```

Inside the guest, give it `10.40.0.50/24`, gateway `10.40.0.1`, DNS `10.40.0.1`.
It can reach the internet through NAT and cannot reach the LAN; pf already
enforces that, and the bridge has no physical member, so there is no layer-2
path either.

### 13.4 What bhyve is and is not

| Property | Reality |
| --- | --- |
| Device model | virtio only; no USB or PCI passthrough configured |
| Network | one virtio NIC on an internal bridge |
| Storage | a file or zvol inside `zroot/vm` |
| Isolation | a separate kernel and userland per guest |
| Security boundary | **no**, not against a hostile guest with a bhyve/kernel bug |

Use a VM for another operating system, for a disposable analysis environment,
or for something you would not run in a jail. Do not treat it as a stronger
sandbox than the host kernel actually provides: on FreeBSD both jails and bhyve
share the host kernel, and only a separate machine is a boundary against a
kernel-level attacker.

### 13.5 Boot behaviour

```sh
sysrc vm_enable=YES
vm list
vm start guest
```

Guests do not autostart by default. If this machine is a gateway first, leave
it that way: a broken guest should never delay the router's boot.

### 13.6 Checkpoint

```sh
bectl create phase13-done
```

---

## Phase 14 — monitoring, audit, integrity

### 14.1 `blacklistd` for SSH

```sh
sysrc blacklistd_enable=YES
install -m 600 /dev/null /etc/blacklistd.conf
cat > /etc/blacklistd.conf <<'EOF'
[local]
ssh stream * * * * 3 24h
EOF
service blacklistd start
pfctl -a 'blacklistd/*' -sr
```

The `anchor "blacklistd/*"` line already exists in `pf.conf`; without it the
daemon has nowhere to add its blocks. Test from a LAN client with three bad
logins and confirm the address appears:

```sh
pfctl -t bruteforce -T show
pfctl -a 'blacklistd/*' -sr
```

### 14.2 Daily checks that write to root's mailbox

`/etc/periodic.conf`:

```sh
daily_status_security_pkgaudit_enable="YES"
daily_status_security_pkgaudit_expiry="2"
daily_status_zfs_enable="YES"
daily_status_zfs_zpool_list_enable="YES"
```

```sh
pkg audit -F
```

Anything reported here is already installed on the machine; treat it as an
outage, not as a warning for the weekend.

### 14.3 Disk health

```sh
pkg install -y smartmontools
sysrc smartd_enable=YES
cat > /usr/local/etc/smartd.conf <<'EOF'
DEVICESCAN -a -m root -M exec /usr/local/sbin/smartd-mail
EOF
service smartd start
smartctl -a /dev/ada0 | head -20
```

If `/usr/local/sbin/smartd-mail` does not exist, drop `-M exec` and let smartd
write to syslog; the point is that a failing disk produces a log line before it
produces a dead gateway.

### 14.4 Integrity of configuration

`mtree` is in the base system and needs no daemon. Take a hash of `/etc` now,
and compare after any suspicious event:

```sh
mtree -c -p /etc -f /root/baseline/etc.mtree
mtree -p /etc -f /root/baseline/etc.mtree | head
```

The first command records; the second reports differences. Store
`/root/baseline/` off the machine too — an attacker with root can edit both the
file and its reference copy.

### 14.5 Log review, weekly

```sh
grep -i 'invalid user\|Failed password' /var/log/auth.log | tail
pfctl -si | grep -E 'block|pass|match'
tcpdump -ni pflog0 -c 50 -e
last -n 20
```

`tcpdump` on `pflog0` is the fastest way to answer "what is this machine
actually dropping"; it is also the only way to notice a rule that is too wide
before someone else does.

### 14.6 Checkpoint

```sh
bectl create phase14-done
```

---

## Phase 15 — updates without gambling

### 15.1 The order

The base system and the packages must not drift apart, and the kernel and its
modules must be built for the running kernel. The safe sequence is always the
same:

```sh
bectl create pre-update-$(date +%Y%m%d)
freebsd-update fetch
freebsd-update install          # kernel and kernel modules
reboot
freebsd-update install          # userland, after the new kernel is running
pkg update
pkg upgrade -y
etcupdate -n                    # preview merges into /etc
etcupdate -B                    # apply, keeping your edits
```

`freebsd-update` is for `-RELEASE` only. If `freebsd-version -kru` shows
`-STABLE` or `-CURRENT`, you update from source and this section does not apply.

Check the machine agrees with itself afterwards:

```sh
freebsd-version -kru
uname -K
pkg check -Ba
```

`freebsd-version -kru` printing three different versions means the reboot in
the middle was skipped. Do not postpone it; a new userland on an old kernel is
exactly the state that produces unexplained `ENOSYS` failures.

### 15.2 Quarterly or latest

FreeBSD's default pkg repository is `quarterly`, which is the right default for
a router: tested together, updated four times a year. NVIDIA drivers and
Chromium land in `latest` first. Choose one deliberately and write it down:

```sh
mkdir -p /usr/local/etc/pkg/repos
cat > /usr/local/etc/pkg/repos/FreeBSD.conf <<'EOF'
FreeBSD: {
  url: "pkg+https://pkg.freebsd.org/${ABI}/quarterly",
  mirror_type: "srv",
  signature_type: "fingerprints",
  fingerprints: "/usr/share/keys/pkg",
  enabled: yes
}
EOF
pkg update -f
```

If a Chromium or GPU regression blocks you, switch that one line to `latest`
until the next quarter, then switch back. Mixing both repositories in one
system is how you get a package set that no one has tested.

### 15.3 Reboot policy

Reboot after every kernel, NVIDIA module or `vmm` update, and after every
`freebsd-update install` that touched the kernel. This machine is a router;
a scheduled five-minute window at a quiet hour is cheaper than a silent
mismatch. Boot environments make the window reversible:

```sh
bectl list
bectl activate pre-update-20261103
reboot
```

---

## Phase 16 — backups that survive the machine

### 16.1 Snapshots on the pool

Snapshots are not backups, but they are the first line and they cost nothing.
`/usr/local/sbin/snapshot-daily`:

```sh
#!/bin/sh
set -eu
stamp=$(date +%Y-%m-%d)
zfs snapshot -r "zroot@daily-$stamp"
zfs list -H -t snapshot -o name -r zroot \
  | grep '@daily-' | sort -r | tail -n +8 \
  | while read -r snap; do zfs destroy "$snap"; done
```

The last line **destroys** every daily snapshot older than the newest seven.
Read it twice before installing the script; a typo in the filter is a deleted
history. Verify with `zfs list -t snapshot | grep daily` after the first run.

```sh
chmod 700 /usr/local/sbin/snapshot-daily
cat >> /etc/crontab <<'EOF'
15 2 * * * root /usr/local/sbin/snapshot-daily
EOF
```

### 16.2 A copy that is not on this disk

A snapshot on `zroot` dies with the pool. Send it to a second disk, weekly, and
verify the receive:

```sh
zfs create -o mountpoint=/backup/offsite backup/offsite 2>/dev/null || true
zfs send -R zroot@daily-$(date +%Y-%m-%d) | zfs receive -F backup/offsite
zfs list -r backup/offsite | head
```

For a remote copy, the same command over SSH (`zfs send -R ... | ssh host zfs
receive -F pool/name`). Either way, a backup that has never been restored is a
hypothesis, not a backup: once a year, receive it into a scratch dataset and
compare a few files.

### 16.3 The small, critical files

```sh
stamp=$(date +%Y-%m-%d)
tar -czf /backup/etc-$stamp.tar.gz \
  /etc /usr/local/etc /var/unbound /var/db/kea /root/baseline
```

This archive is what you actually need after a reinstall: pf rules, jail.conf,
unbound and Kea config, doas, sshd, and the hashes. It contains no private keys
if you excluded `/etc/ssh` — do not exclude it if you want a same-day restore,
but then treat the archive as a secret.

### 16.4 What is not backed up

Chromium's cache, `/tmp`, package caches and VM disk images are deliberately
absent: they are large, reproducible or both. VM images are the exception you
must decide on explicitly; if a guest holds state, add `/vm` to the send list
and accept the size.

### 16.5 Checkpoint

```sh
bectl create phase16-done
```

---

## 17. Operating the machine

### 17.1 Cadence

| When | What | Command or place |
| --- | --- | --- |
| daily (automatic) | package audit, ZFS status, SMART | root's mail from `periodic` |
| daily (2 min) | states, drops, jails, pool | `pfctl -si`, `zpool status -x`, `jls` |
| weekly | updates, log review, snapshot count | phase 15, phase 14.5 |
| monthly | `zpool scrub`, restore one file, read the pf rules again | `zpool scrub zroot` |
| quarterly | rotate SSH keys, re-read the jail and pf config, check `bectl list` | — |

### 17.2 Change procedure

Every change, however small, in this order:

```sh
bectl create change-$(date +%Y%m%d-%H%M)
# edit exactly one thing
pfctl -nf /etc/pf.conf          # or the matching syntax check
# apply
# verify with the command from the phase that owns the setting
```

If a change cannot be described in one sentence and verified with one command,
it is two changes. Split it.

### 17.3 Incident response

Assume compromise of the host, not of a jail, until proven otherwise.

```sh
# 1. isolate, do not reboot yet
ifconfig em0 down
printf 'block all\n' | pfctl -f -

# 2. preserve what is volatile
zfs snapshot zroot@incident-$(date +%Y%m%d-%H%M)
cp /var/log/auth.log /var/log/messages /backup/
pfctl -sr > /backup/pf.incident.txt
netstat -an > /backup/netstat.incident.txt
ps aux > /backup/ps.incident.txt
sockstat -4 -l > /backup/sockstat.incident.txt

# 3. scope: host, jail or VM?
jls
last -n 30
```

Then decide, in this order:

- **A jail or VM only?** Destroy it from the clean template, keep the host.
- **Host userland only?** `bectl activate` the last known-good environment and
  diff `/etc` against `/root/baseline/etc.mtree`.
- **Root on the host?** Rebuild from installation media. Do not trust binaries,
  boot environments or backups created after the compromise; rotate every key
  that was on the machine (SSH host keys, authorized keys, any token in the
  browser profile).

A reboot before step 2 destroys the evidence. Isolate first, snapshot second,
reboot never until you have decided.

---

## 18. Verification checklist

Run this top to bottom after the build, and again after any phase that touches
kernel, network or authentication. Every line has an expected result; a line
that differs is a defect, not a warning.

```sh
# kernel state
sysctl kern.smp.hyperthreading_allowed   # 0
sysctl -n hw.ncpu                        # 6
sysctl kern.elf64.allow_wx               # 0
sysctl kern.securelevel                  # 1
sysctl hw.mds_disable                    # 1
kldstat -m nvidia-modeset                # listed
kldstat -m vmm                           # listed

# storage
zpool status -x                          # "pool is healthy"
zfs get -H -o value compression zroot    # lz4
zfs get -H -o value atime zroot          # off
swapinfo -h                              # encrypted device, size > 0

# network and firewall
ifconfig em0 | grep 'inet '              # WAN address
ifconfig igc0 | grep 'inet '             # 10.20.0.1
netstat -rn -f inet | head -3            # default via em0
pfctl -sr | grep -c 'block'              # > 0
pfctl -si | grep 'Status'                # Enabled
pfctl -t bruteforce -T show              # empty or explained

# services
sockstat -4 -l                           # only ssh 22, dns 53, dhcp 67 on LAN addresses
service -e | grep -E 'sshd|unbound|kea|pf|jail' 

# DNS and time
drill @127.0.0.1 freebsd.org             # answer
drill @127.0.0.1 dnssec-failed.org       # SERVFAIL
ntpq -p                                  # at least one '*'

# jails and VMs
jls                                      # web, state ACTIVE
jexec web drill @10.30.0.1 freebsd.org   # answer
jexec web nc -vz 10.20.0.10 22           # refused or timeout
vm list                                  # guest, state Stopped or Running

# desktop
glxinfo | grep 'OpenGL renderer'         # NVIDIA, not llvmpipe
ls /home/admin/.config/i3/config         # present
```

Two checks that need a second machine, not a command:

1. From a LAN client: `ssh admin@10.20.0.1` works, `ssh admin@<wan-ip>` does not.
2. From outside: a port scan shows 22 filtered and 80/443 reaching the jail,
   nothing else.

---

## 19. Trade-offs, written down so they are choices

| Decision | You gain | You give up |
| --- | --- | --- |
| SMT off | sibling-thread side channels closed | ~20–30% on parallel work; 6 CPUs instead of 12 |
| `allow_wx=0` | no writable-executable mappings | JIT software may need `elfctl` per binary |
| `securelevel=1` | no runtime module loading, no raw disk writes | driver tests need a reboot; some services cannot be started ad hoc |
| `blackhole` | scans get no answer | local clients see timeouts instead of refusals |
| `unprivileged_proc_debug=0` | no cross-user `ptrace` | crash reporters and cross-user debuggers stop working |
| no IPv6 | a whole protocol family cannot be attacked | any IPv6-only service is unreachable; revisit if the ISP moves |
| SSH on LAN only | no brute force from the internet | remote work needs WireGuard or a console |
| no display manager | one less root service, no login greeter | `startx` after every console login |
| iGPU off | one driver, less surface, lower idle power | no QuickSync transcoding |
| ARC capped at 6 GiB | the desktop never waits on cache reclaim | colder ZFS cache than a server build |
| jails share the kernel | cheap, fast, good isolation of services | a kernel exploit is not contained |

If you disagree with one of these, change it in the phase that owns it and
update this table. The failure mode to avoid is a machine that is neither fast
nor hardened because nobody wrote down which knob was flipped and why.

---

## Appendix A — files this runbook creates or edits

| Path | Owns |
| --- | --- |
| `/boot/loader.conf` | SMT, W^X, ASLR, mitigations, ARC, modules |
| `/etc/sysctl.conf` | stack and kernel hardening, `kern.securelevel` |
| `/etc/rc.conf` | interfaces, forwarding, pf, services, `dumpdev` |
| `/etc/pf.conf` | the firewall, NAT and the one published service |
| `/etc/devfs.rules` | raw disk modes |
| `/etc/jail.conf` | jail capabilities and vnet wiring |
| `/etc/rctl.conf` | per-jail resource caps |
| `/etc/blacklistd.conf` | SSH brute-force response |
| `/etc/ntp.conf` | time sources and LAN restrictions |
| `/etc/ssh/sshd_config` | the only administrative path |
| `/etc/periodic.conf` | what root is mailed about |
| `/var/unbound/unbound.conf` | validating resolver, LAN listeners |
| `/usr/local/etc/kea/kea-dhcp4.conf` | DHCP pool and options |
| `/usr/local/etc/pkg/repos/FreeBSD.conf` | quarterly vs latest |
| `/usr/local/etc/X11/xorg.conf.d/20-nvidia.conf` | NVIDIA device and screen |
| `/usr/local/etc/X11/xorg.conf.d/00-keyboard.conf` | X keyboard layout |
| `/home/admin/.xinitrc`, `/home/admin/.config/i3/config` | the desktop |
| `/usr/local/sbin/snapshot-daily` | daily snapshots and retention |
| `/root/baseline/` | the before-state and the `/etc` hash tree |

## Appendix B — packages, by purpose

| Purpose | Packages |
| --- | --- |
| privilege | `doas` |
| CPU | `cpu-microcode` |
| DHCP | `kea` |
| GPU | `nvidia-driver`, `nvidia-settings` |
| desktop | `xorg`, `i3`, `i3status`, `dmenu`, `xterm`, `chromium`, `dejavu`, `xorg-fonts-truetype` |
| virtualisation | `vm-bhyve` |
| health | `smartmontools` |
| measurement | `hyperfine`, `mesa-demos` |
| optional remote | `wireguard-tools` |
| optional jail managers | `bastille`, `pot` |

Nothing in this list pulls in a Linux compatibility layer, a display manager or
a desktop environment. That is intentional.

## Appendix C — pf cheat sheet

```sh
pfctl -nf /etc/pf.conf        # parse, do not apply
pfctl -f /etc/pf.conf         # apply
pfctl -d                      # disable entirely (console escape hatch)
pfctl -e                      # re-enable
pfctl -sr                     # rules as loaded
pfctl -si                     # counters and state table
pfctl -ss                     # live states
pfctl -t bruteforce -T show   # table contents
pfctl -t bruteforce -T flush  # empty it
pfctl -a 'blacklistd/*' -sr   # blacklistd's own rules
pfctl -F all                  # flush states, tables and rules
```

`pfctl -F all` without a reload leaves the machine passing everything. Never
run it over SSH on a machine you cannot reach with a console.

## Appendix D — `GFX0`, `DD1F`, and what ACPI names are good for

Short answer: `GFX0` and `DD1F` are **labels in the ACPI namespace**, not
driver options and not tunables. They are useful for diagnosis and useless for
performance or security.

- `GFX0` (sometimes `IGPU` on newer Intel platforms) is the ACPI device that
describes the PCI graphics function. It shows up in `acpidump -dt` and in
  `dmesg` paths like `\_SB.PCI0.GFX0`.
- `DD1F` is one of the **display output devices** under it — the firmware's
  description of a connector/panel. `acpi_video(4)` binds to those `DD0x`
  children to implement brightness and DPMS on firmware that exposes them.

On this machine, with a desktop NVIDIA card and no panel, `acpi_video` is not
part of the working path: the NVIDIA driver owns the outputs, and brightness
keys are a laptop concern. So:

- Do **not** add `acpi_video_load="YES"`. Two owners for one output is how you
  get a black screen on resume or a display that ignores DPMS.
- Do look at the names when something ACPI-shaped is wrong:
  `dmesg | grep -i acpi_video`, `sysctl hw.acpi.video`, `acpidump -dt | grep -n
  GFX0`. That is the whole value of `GFX0`/`DD1F` here.
- If the machine ever develops a brightness problem, the diagnostic is
  `sysctl hw.acpi.video` and the fix belongs in the driver or firmware
  configuration, not in a pf or sysctl hardening file.

## Appendix E — names that recur

| Term | What it is on FreeBSD |
| --- | --- |
| MAC | TrustedBSD pluggable access-control policies (`mac_*` modules) |
| Capsicum | capability mode (`cap_enter`), used by Chromium and base tools |
| jail | kernel-enforced namespace isolation for processes, sharing the host kernel |
| vnet | a jail with its own network stack |
| `epair` | the virtual Ethernet pair connecting a vnet jail to a bridge |
| bhyve | the userspace hypervisor |
| `vmm(4)` | on FreeBSD, bhyve's kernel driver; on OpenBSD, a different hypervisor |
| boot environment | a ZFS clone of the root dataset that the loader can boot |
| securelevel | a monotonic kernel restriction level; 1 blocks module loads and raw disk writes |
| W^X | no memory mapping both writable and executable |
| ASLR | randomised address space layout |
| `rctl` | resource limits per jail, user or process |
| pf anchor | a named sub-ruleset that a daemon can edit without touching `pf.conf` |

---

End of runbook. A machine built by following this document, top to bottom, ends
with: six CPUs, an encrypted swap, a default-deny router with one published
jail, a validating resolver, key-only SSH on the LAN, an i3 desktop on the
NVIDIA driver, and a boot environment you can return to. Everything after that
is maintenance, and section 17 is the maintenance.

