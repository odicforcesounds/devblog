# ADD GPG Key to Profile

Create or Setup your GPG key

```sh
gpg --full-generate-key --expert
```

Create a Recocation certificate

```sh
gpg --output ~/.gnupg/revocation.crt --gen-revoke mysupercool@email.net
chmod 600 ~/.gnupg/revocation.crt # Change permissions
```

See what is our Public Key

```sh
gpg --output ~/.gnupg/publickey.key --armor --export mysupercool@email.net
```

See keys

```sh
gpg --list-keys
```

Publish public-key

```sh
gpg --send-keys --keyserver pgp.mit.edu mykey
```

Add public-key.key to codeberg profile

```sh
just follow their instructions
```

Setup some of the files needed for pinentry settings

```sh
touch .gnupg/gpg-agent.conf
touch .gnupg/gpg.conf
```

Create content in gpg-agent.conf

```
max-cache-ttl 60480000
default-cache-ttl 60480000
```

Create content in gpg.conf

```
personal-digest-preferences SHA512
cert-digest-algo SHA512
default-preference-list SHA512 SHA384 SHA256 SHA224 AES256 AES192 AES CAST5 ZLIB BZIP2 ZIP Uncompressed
personal-cipher-preferences TWOFISH CAMELLIA256 AES 3DES
```

Add to Your .bashrc file

```
export GPG_TTY=$(tty)
gpg-connect-agent updatestartuptty /bye >/dev/null
```

> Any other issue, please read ArchLinux documentation about it: https://wiki.archlinux.org/title/GnuPG#pinentry

Add your GPG key to your ~/.gitconfig file

```sh
$ git config --global user.signingkey yourShort/LongKeyID
```
