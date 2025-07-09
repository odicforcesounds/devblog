<h1> LVM </h1>

Use LVM to defined dynamic partitions

```sh
$ sudo lvmdiskscan
$ sudo pvcreate /dev/mapper/distro
$ sudo pvdisplay
$ sudo vgcreate distro /dev/mapper/distro
$ sudo vgdisplay
$ sudo lvcreate -C -y -L 2G distro -n swap
$ sudo lvcreate -L 90G -n root
$ sudo lvcreate -l +100%FREE distro -n home
$ sudo lvdisplay
$ sudo vgscan 
$ sudo vgchange -ay

```


