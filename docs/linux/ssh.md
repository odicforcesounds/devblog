# SSH

## Client-side

SSH is for secure communications. 

If you are using Linux, ensure you create your personal key.

```sh
ssh-keygen
```

Your new Private SSH-KEY was stored in  $HOME/.ssh folder. 

You can create more to different hosts. Be sure you put your new ssh-keys into ~/.ssh/

You can use **scp** to transfer files from server to client or client or server. 

---

## Server-side

You can configure ssh to run as a server, into any machine you wish to connect using ssh. 

Edit:
```sh
vim /etc/ssh/sshd_config
```
  - Recommended: 

    1. Forbid root logins
    2. copy your public key to ssh-server
    3. Forbid logins with password
    4. accept only known public keys connections


