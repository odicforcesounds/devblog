# Secure Shell Daemon

While SSH is what you need to manage any remote Linux server, SSH is one of the first target points of random attacks made by Bots. Sometimes you can configure ssh-service to add some delay from each login-failure, but since this kind of attacks happen every single minute, when you read the logs you see how annoying this is. So, the best approach is to limit users to use a public key and limit ssh-logins to this method, excluding all password based logins. The attacks continue, but now you don't need to worry about them. 

I configure fail2ban to ban users for **-1** days ( Eternal-ban ) and even if root logins are forbidden, sometimes I see that this "bots" are trying to use some names, like admin, test, user, ubuntu, etc., which lead me to believe that they will have some luck and find the name of the users in [this server](./greatsky.md) I am self-hosting. 

There are a lot of articles that explain how to secure your ssh-service, but I wish to add this tips right here for you, dear reader. 

```bash 
# /etc/ssh/sshd_config 
PermitRootLogin no
ChallengeResponseAuthentication no 
PasswordAuthentication no 
UsePam no 
AuthenticationMethods publickey 
PubkeyAuthentication yes 
AllowUsers userA userB userC 
DenyUsers root toor suck fuck luck 
PermitEmptyPasswords no 
ClientAliveInterval 300 
ClientAliveCountMax 0
Banner no 
IgnoreRhosts yes 
HostbasedAuthentication no
```

With this configuration, I am in peace with all those random botnets attacks, which sometimes make me believe that are real persons trying their luck. (oh fuck) 

Now I wish them a best luck in the world. :) 
