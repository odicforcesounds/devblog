# Setup SSH-key to use with git

Create your ssh-key associated with your email

```sh
ssh-keygen # Use the email used by the same repository
```

Setup ssh-agent

```sh
eval `ssh-agent`
```

Verify your account

```sh
ssh -vT user@codeberg.org
```

push without using passwork or token

```sh
git push # use token as user and passwd is possible
```
