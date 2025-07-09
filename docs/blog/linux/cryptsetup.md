<h1> Cryptsetup </h1>

Use to encript hard-disk

If You are paranoid, be sure you format full disk as: 

```sh
$ sudo dd if=/dev/urandom of=/dev/sda status=progress; sync
$ sudo dd if=/dev/zero of=/dev/sda status=progress; sync
```

Create partition with cfdisk or fdisk and encrypt selected partition


```sh
$ sudo cryptsetup -v -y -c aes-xts-plain64 -s 512 -h sha512 -i 5000 --use-random luksFormat /dev/sdX(3)
```

Then Open encripted partition using defined passwd 

```
$ sudo cryptsetup lukDump /dev/sdaX > saveDump.txt
$ sudo cryptsetup luksOpen /dev/sdaX lvm
```

