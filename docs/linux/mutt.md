<h1> email-client/mutt </h1>

<h3> Celebrating 25 Years </h3>

- http://www.mutt.org/

Used to manage email boxes. 

<h2> install mutt </h2>

```sh
# debian based
$ sudo apt install mutt msmtp isync abook
# gentoo based
$ sudo emerge -av mutt msmtp isync abook
```

Configure $HOME/.mutt

```sh
$ mkdir .mutt
$ cd .mutt
$ touch muttrc 
```

Configure $HOME/.mutt/muttrc file

```sh
set imap_user = user@mail.org
set imap_pass =`pass show user@mail.org`
set realname = username
set from = "user@mail.org"
set folder = imaps://imap.mail.org
set smtp_url = smtps://user@mail.org@smtp.mail.org
set ssl_force_tls = yes
set spoolfile = +INBOX
set record = "+Sent"
set postponed = "+Drafts"
set trash = "+Trash"
set editor = "vim"
set sendmail="/usr/bin/msmtp"
```

Configure $HOME/.msmtprc 

```sh
defaults
port 597
tls on
tls_certcheck on
tls_trust_file /etc/ssl/certs/ca-certificates.crt
account my-email
host smtp.email.org
from user@mail.org
auth on
user user@mail.org
account default : my-email
passwd `pass show user@mail.org`
```




