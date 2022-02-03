# GNUPG

Tools to sign data and encrypt data. 

Save your secrets, encripted. 

Protect encripted data with password

Desencrypt your secrets only when needed. 

```sh
gpg --full-generate-key
```
Follow instructions:

1. Add the email you are going to use for email
2. Use RSA key
3. Set a password


Create **revocation** certificate if you want to remove old gpg-key.

```sh
gpg --output ~/revocation.crt --gen-revoke yourEmail
# 
chmod 600 ~/revocation.crt
```
See your gpg keys: 

```sh
gpg --list-keys
```


Share Public key: 

```sh
gpg --output ~/username.key --armor --export user@email 
```

Set your public key access in public server

```sh
gpg --send-keys --keyserver pgp.mit.edu YOURKEY
```

Encript files: 

```sh
gpg --encrypt --sign --armor -r user@mail file.txt
```

Deincript files

```sh
gpg --decrypt file.asc > plain.txt
```
