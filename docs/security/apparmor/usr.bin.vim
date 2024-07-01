#include <tunables/global>

/usr/bin/vim {
  # Include necessary abstractions
  #include <abstractions/base>
  #include <abstractions/nameservice>
  #include <abstractions/user-tmp>

  capability,
  network,
  
  /bin/** rmix,
  /usr/bin/** rmix,
  /usr/local/bin/** rmix,
  /sbin/** rmix,
  /usr/sbin/** rmix,
  
  /lib/** rm,
  /lib64/** rm,
  /usr/lib/** rm,
  /usr/lib64/** rm,

  /etc/ld.so.cache r,
  /etc/ld.so.conf r,
  /etc/ld.so.conf.d/ r,
  /etc/nsswitch.conf r,
  /etc/passwd r,
  /etc/group r,
  /etc/hostname r,
  /etc/hosts r,
  /etc/resolv.conf r,
  
  /dev/tty rw,
  /dev/null rw,
  /dev/urandom r,

  /tmp/** rw,
  /var/tmp/** rw,

  owner @{HOME}/** rwk,

  deny /etc/shadow r,
  deny /etc/gshadow r,

  deny /proc/** rw,
  deny /sys/** rw,
}

