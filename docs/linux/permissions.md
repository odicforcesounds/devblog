# Linux Permissions

All tools and software you need is installed. 

- Disable Compilers
```
chmod 000 /usr/bin/as >/dev/null 2>&1
chmod 000 /usr/bin/cc >/dev/null 2>&1
chmod 000 /usr/bin/gcc >/dev/null 2>&1
chmod 000 /usr/bin/c++ >/dev/null 2>&1
chmod 000 /usr/bin/g++ >/dev/null 2>&1
# chmod 000 /usr/bin/byacc >/dev/null 2>&1
# chmod 000 /usr/bin/yacc >/dev/null 2>&1
# chmod 000 /usr/bin/kgcc >/dev/null 2>&1
``` 

- Restrict read access 

```
# System Logs 
chmod -R g-wx,o-rwx /var/log/*
chown root:root /var/log/*

# ssh Server Config files
chmod og-rwx /etc/ssh/sshd_config
chown root:root /etc/ssh/sshd_config

# passwd file
chmod 644 /etc/passwd
chown root:root /etc/passwd

# Shadow file 
chmod o-rwx,g-wx /etc/shadow
chown root:root /etc/shadow

# group's file 
chmod 644 /etc/group
chown root:root /etc/group

# gshadow
chmod o-rwx,g-rx /etc/gshadow
chown root:root /etc/gshadow

# passwd file
chmod 644 /etc/passwd-
chown root:root /etc/passwd-

# Shadow file 
chmod o-rwx,g-wx /etc/shadow-
chown root:root /etc/shadow-

# group's file 
chmod 644 /etc/group-
chown root:root /etc/group-

# gshadow
chmod o-rwx,g-rx /etc/gshadow-
chown root:root /etc/gshadow-
```

- Restrict Virtual Partitions

```
mount -o remount,noexec /tmp
mount -o remount,rw,hidepid=2 /proc
mount -o remount,noexec /dev
mount -o remount,nodev /run 
```


