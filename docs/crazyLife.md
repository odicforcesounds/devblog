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

If you are a client, create your ssh-key in your local machine. 

```bash
ssh-genkey 
# Give a name to identify that key: my-ssh-server
```

Copy that key to your server 

```bash 
ssh-copy-id -i ~/.ssh/server username@serverAddress
# insert password
```

Now connect to your server without using a password 

```bash
ssh -i ~/.ssh/server 'username@serverAddress'
```

On your server side, change your ssh files permissions. 

```bash 
chmod 700 ~/.ssh 
chmod 600 ~/.ssh/known_hosts
```

Change sshd_config file: 

```bash
# /etc/ssh/sshd_config
PubKeyAuthentication yes
```

No connections are possible without using ssh-keys. 

Happy SSH sessions. 
