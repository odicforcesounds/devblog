gpg --version
gpg (GnuPG) 2.0.22

eval $(gpg-agent --daemon) -> make sure gpg-agent is running
gpg-agent -> Check if gpg-agent is running

gpg --gen-key -> generate a GPG key pair 
gpg --list-secret-keys --keyid-format LONG -> List public and private key GPG keys.
                                              A private key is required for signing commits or tags.
gpg --delete-secret-keys 3AA5C34371567BD2 -> delete secret keys

sec   4096R/3AA5C34371567BD2 2016-03-10 [expires: 2017-03-10] -> Copy the GPG key ID

gpg --armor --export 3AA5C34371567BD2 -> Copy GPG key -----BEGIN PGP PUBLIC KEY BLOCK----- and 
                                         ending with -----END PGP PUBLIC KEY BLOCK-----

git config --global user.signingkey 3AA5C34371567BD2 -> Set GPG signing key in Git,substituting in the GPG key ID 
git config --global commit.gpgsign true

echo 'export GPG_TTY=$(tty)' >> ~/.bashrc -> Add your GPG key to your bash profile

gpg --edit-key 3AA5C34371567BD2 -> Associatean email with GPG key
gpg> adduid -> GPG console, enter && save && exit

gpg --armor --export 3AA5C34371567BD2 -> copy and paste public key on github

git commit -S -m 'your commit message' -> Add the -S flag to the git commit command
git push -> Push them to your remote repository on GitHub
git tag -s v1.0 -> To sign a tag, add -s
git tag -v v1.1 -> Verify your signed tag


echo 'no-tty' >> ~/.gnupg/gpg.conf -> Since you are using an agent, you could as a workaround add no-tty to your gpg.conf

gpg-agent -> Check if gpg-agent is running
gpg -s any-file.txt ->  Make sure gpg-agent has your passphrase in cache
rm any-file.txt.gpg ->  Delete the newly generated signed any-file.txt.gpg
git commit -S -m 'my commit message' -> Signing commits with Git works by taking the required passphrase from gpg-agent.



ssh:
create two user accounts on rhel6 server
log in as user1 over ssh
su - root
su - user2
gpg --gen-key (fails)

on console:
login as root
su - user2
gpg --gen-key (fails)

FIX
$ script /dev/null
$ gpg2 --gen-key
--------------------------------------------------------------------------------------
#signature kali repo

#gpg itself has a standard way to distribute keys, 
#using a keyserver that gpg can download a key from and add it to its keyring
gpg --keyserver hkp://keys.gnupg.net --recv-key 7D8D0BF6 

gpg --fingerprint 7D8D0BF6 #Check the fingerprint
/bin/sh -c "gpg -a --export 7D8D0BF6 | apt-key add -" 
apt update

generate a full-fingerprint imported key
apt-key adv --list-public-keys --with-fingerprint --with-colons

#receive a GPG error about the repository key being expired (ED444FF07D8D0BF6).
wget -q -O - https://archive.kali.org/archive-key.asc | apt-key add

--------------------------------------------------------------------------------------
apt-key list
#gpg itself has a standard way to distribute keys, 
#using a keyserver that gpg can download a key from and add it to its keyring
gpg --keyserver subkeys.pgp.net --recv-keys 55BE302B

#export that key from your own keyring and feed it to apt-key
gpg -a --export 55BE302B | sudo apt-key add -

#manually check for package's integrity

wget -q -O - https://ftp-master.debian.org/keys/archive-key-10.asc | sudo apt-key add
--------------------------------------------------------------------------------------
# Download vagrant  binary and signature files.
curl -Os https://releases.hashicorp.com/vagrant/2.0.4/vagrant_2.0.4_x86_64.deb
curl -Os https://releases.hashicorp.com/vagrant/2.0.4/vagrant_2.0.4_SHA256SUMS
curl -Os https://releases.hashicorp.com/vagrant/2.0.4/vagrant_2.0.4_SHA256SUMS.sig
# Verify the signature file is untampered.
gpg --verify vagrant_2.0.4_SHA256SUMS.sig vagrant_2.0.4_SHA256SUMS
# Verify the SHASUM matches the binary.
shasum -a 256 -c vagrant_2.0.4_SHA256SUMS
--------------------------------------------------------------------------------------
$ gpg --verify suricata-5.0.0.tar.gz.sig suricata-5.0.0.tar.gz
gpg: Signature made Mon 14 Oct 2019 02:20:27 PM UTC using RSA key ID 00C1B70D
gpg: Can't check signature: No public key

# gpg: Signature made Mon 14 Oct 2019 02:20:27 PM UTC using RSA key ID 00C1B70D
$ gpg --recv-key 00C1B70D
gpg: requesting key 00C1B70D from hkp server keys.gnupg.net
gpg: /home/vagrant/.gnupg/trustdb.gpg: trustdb created
gpg: key 00C1B70D: public key "Open Information Security Foundation (OISF) <releases@openinfosecfoundation.org>" imported
gpg: no ultimately trusted keys found
gpg: Total number processed: 1
gpg:               imported: 1  (RSA: 1)


$ gpg --verify suricata-5.0.0.tar.gz.sig suricata-5.0.0.tar.gz
gpg: Signature made Mon 14 Oct 2019 02:20:27 PM UTC using RSA key ID 00C1B70D
gpg: Good signature from "Open Information Security Foundation (OISF) <releases@openinfosecfoundation.org>"
gpg: WARNING: This key is not certified with a trusted signature!
gpg:          There is no indication that the signature belongs to the owner.
Primary key fingerprint: 801C 7171 DAC7 4A6D 3A61  ED81 F7F9 B0A3 00C1 B70D
