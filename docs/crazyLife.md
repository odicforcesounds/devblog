# Crazy Life

If you chech Fail2ban logs, the ips change for similar ips, when they are banned. 

Since I change the login attemps to one, at second try they are banned. 

: - 111.22.333.44 scan and blocked 
: - 111.22.333.55 scan and blocked 

Looks like this persons change their IP by releasing their public IP to change to another public IP. 

```bash
# vim /etc/ssh/sshd_config 
```

Some changes to do to secure our server. 

```bash
# /etc/ssh/sshd_config 
PermitRootLogin no
MaxAuthTries 1
PermitEmptyPasswords no 
```

Next is to configure SSH-key in local-client-machine and upload it to the user@server. 

Test and change sshd_config file: 

```bash
# /etc/ssh/sshd_config
PubKeyAuthentication yes
```

No connections are possible without using this keys. 

Happy SSH sessions. 
