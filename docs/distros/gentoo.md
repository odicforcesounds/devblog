```bash
tar xpJf stage3-*.tar.xz --xattrs-include='*.*' --numeric-owner
```

Associar ficheiro de configuração da sincronização dos repositórios públicos

```bash
mkdir -p -v /mnt/gentoo/etc/portage/repos.conf
cp -v /mnt/gentoo/usr/share/portage/config/repos.conf /mnt/gentoo/etc/portage/repos.conf/gentoo.conf
```

Copiar ficheiro de DNS para a partição da instalação

```bash
cp -v -L /etc/resolv.conf /mnt/gentoo/etc/
```

Associar sistemas de ficheiro de acesso a pontos de hardware

```bash
mount -v -t proc none /mnt/gentoo/proc
mount -v --rbind /sys /mnt/gentoo/sys
mount -v --rbind /dev /mnt/gentoo/dev
mount -v --make-rslave /mnt/gentoo/sys
mount -v --make-rslave /mnt/gentoo/dev
```

```bash
chroot /mnt/gentoo /bin/bash -l
```

```bash
passwd
```

```bash
env-update && source /etc/profile && export PS1="(chroot) $PS1"
emerge --sync
```

```bash
eselect profile list
eselect profile set 26 # nomultilib
```

```bash
emerge --ask --verbose --oneshot portage
```

```bash
emerge --ask --verbose portage-utils gentoolkit mirrorselect
```

```bash
echo "Europe/Lisbon" > /etc/timezone
emerge -v --config sys-libs/timezone-data
```

```bash
nano -w /etc/locale.gen
locale-gen
eselect locale set "en_US.UTF-8" # Latin Characters on SHELL PLEASE !!!
env-update && source /etc/profile && export PS1="(chroot) $PS1"
```

```bash
nano -w /etc/conf.d/keymaps # pt-latin9
```

```bash
nano -w /etc/conf.d/hostname # ThinkAbout
```

```bash
COMMON_FLAGS="-O2 -pipe -march=sandybridge"
CFLAGS="${COMMON_FLAGS}"
CXXFLAGS="${COMMON_FLAGS}"
FCFLAGS="${COMMON_FLAGS}"
FFLAGS="${COMMON_FLAGS}"
CPU_FLAGS_X86="aes avx mmx mmxext pclmul popcnt sse sse2 sse3 sse4_1 sse4_2 ssse3"
MAKEOPTS="-j5"
# USE FLAGS
USE="-ipv6 -bindist vim-pager vim-syntax savedconfig"
# Features
FEATURES="split-elog buildpkg"
# Licenses
ACCEPT_LICENSE="-* @FREE"
# Video Card
VIDEO_CARDS="intel i915"
# Audio Card
ALSA_CARDS="snd-hda-intel"
# Inputs
INPUT_DEVICES="libinput"
# Keywords
ACCEPT_KEYWORDS="amd64" # only stable versions
# Grub
GRUB_PLATFORMS="pc"
# LLVM Targets
LLVM_TARGETS="x86 BPF"
# Portage system
PORTAGE_ELOG_CLASSES="info warn error log qa"
PORTAGE_ELOG_SYSTEM="echo save"
EMERGE_DEFAULT_OPTS="--ask --verbose"
PORTAGE_NICENESS=10
# ADD Language
L10N="pt pt_PT"
# Portage Directories
PORTDIR="/var/db/repos/gentoo"
DISTDIR="/var/cache/distfiles"
PKGDIR="/var/cache/binpkgs"
LC_MESSAGES=C
```

Recommended Packges:

```
app-editors/vim
app-misc/abook
app-misc/tmux
app-misc/vifm
app-office/calcurse
app-portage/eix
app-portage/gentoolkit
app-portage/portage-utils
app-text/grip
dev-vcs/git
mail-client/mutt
mail-mta/msmtp
media-video/ffmpeg
media-video/mplayer
net-firewall/ipset
net-firewall/iptables
net-libs/nodejs
net-mail/isync
net-mail/mailbase
net-mail/rss2email
net-misc/curl
net-misc/dhcp
net-misc/yt-dlp
net-firewall/iptables
net-irc/irssi
net-wireless/wpa_supplicant
sys-fs/dosfstools
sys-fs/e2fsprogs
sys-fs/fuse
sys-fs/mtpfs
sys-process/htop
sys-process/lsof
www-client/lynx
www-client/w3m
```
