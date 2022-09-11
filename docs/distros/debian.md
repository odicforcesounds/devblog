# Debian 

Minimal instalation guide for old laptops 

1. Download ISO image 
2. Flash ISO image into USB stick
- dd if=debian-minimal.iso of=/dev/sdx; sync
3. Setup BIOS to boot from USB 
4. Boot USB with ISO image
5. Setup root password and add default user
6. Setup Partitions using cfdisk
- For paranoid security we start defining several partitions. 
- Lets imagine we have a 512GB Hard drive
  1. /boot/ - 200MB - IF BIOS EXT2/3/4 - IF UEFI FAT32
  2. / - 20GB EXT4
  3. /var - 20GB EXT4
  4. /var/log - 20GB EXT4
  5. /usr - 20GB EXT4
  6. /tmp - 10GB EXT4
  7. none - 2GB SWAP 
  8. /home - 100%FREE 
7. Continue 
- We don't select a default desktop 
- Select SSH Server to boot with by default
8. Install grub into your main hard drive 
9. Reboot and remove USB disk 
10. Connect to the machine with: 'ssh user@host/ip'
- By default the default user is in the wheel group. We can su in: 'su -l' 
11. Software Installation: apt update && apt upgrade -y 
- Use 'apt search' to search packages, and 'apt install' to install them
- By default debian use the nano editor ( no vim ): 'apt install vim'
I really like this example
```sh
wget https://raw.githubusercontent.com/sd65/MiniVim/master/vimrc 
```

Install more useful software for our laptop

```sh
apt install \ 
cpufreq iptables tuned htop iotop strace lm-sensors fancontrol i2c-tools \
dosfstools git newsboat flawfinder pscan 
```
12. Manager boot services with: 'update-rc.d' / 'service --status-all'
13. Setup cpufreq with: 'cpufreq-set -g powersave'
14. Block kernel-image upgrades with: 'apt-mark hold linux-image-{version}'
15. Block kernel-headers upgrades with: 'apt-mark hold linux-headers-{version}'
16. Edit /etc/fstab and setup permissions to secure partitions
- /boot ro
- /home defaults,nosuid,nodev,async,auto
- /tmp defaults,nosuid,noexec,nodev
- /usr defaults,ro,nodev,nosuid
- /var defaults,ro,nodev
- /var/log defaults,nodev,nosuid,noexec
17. Setup IPTables: 
- https://tldp.org/HOWTO/Security-Quickstart-HOWTO/
- https://tldp.org/HOWTO/Security-HOWTO/
- https://tldp.org/HOWTO/IPCHAINS-HOWTO.html
- https://tldp.org/HOWTO/Firewall-HOWTO.html
- https://tldp.org/HOWTO/Secure-Programs-HOWTO/
18. Don't let root ssh into the machine
- https://tldp.org/HOWTO/Security-HOWTO/
- 'vim /etc/ssh/sshd config': Permit root Login: NO

