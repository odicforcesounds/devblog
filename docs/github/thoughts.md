---
tags: [git, github, security, features, privacy]
---

<h1> Thinking About... </h1>

<h2> Github.com</h2>

1. If user use ssh, don't need to use a token.
2. If User is using a token, he/she can modify .gitconfig with any email and that email is used to push request.

```sh
 This lead 'us' to think:
```

- Monkey can create one repository and emulate several contributions - Users may exist or not : email@email.com

<h3> Monkey Naughty Thoughts </h3>

- Monkey can have one repo with several contributions from different users..

        - Oh.. this repository have a lot of contributions...

- Monkey can be other user.. ( hidden / visual-proxy ) to the eyes of other users / visitants.

This is what I call a **AWESOME** Privacy Feature!!

---

Sharing my own configurations

```

[user]
  name = "Monkey Style"
[transfer]
  fsckobjects = true
[fetch]
  fsckobjects = true
[receive]
  fsckobjects = true
[push]
  default = simple
  followTags = true
[color]
  branch = auto
  diff = auto
  status = auto
  ui = true
[credential]
  username = gh.....................................
  password = gh.....................................
  helper = cache --timeout=3000
[core]
  editor = vim
  pager = less -F -X
  gitProxy = ssh
[init]
  templatedir = ~/.git_template
[pull]
	rebase = false
```

You may see this repository history.. I am playing around :D

--- 

Just forget the last approach. Use SSH-KEYS !!!  

```sh 
eval $(ssh-agent)
ssh-add ~/.ssh/github 
push git@github.com:ABC/REPO
```


