# Debian Upgrade 

## Bookworm to Trixie 

First be sure you have your bookworm full-updated. 

```bash 
sudo apt update 
sudo apt upgrade -y
sudo apt full-upgrade -y
```

After than, you need to change the name of the sources at /etc/apt/sources.list

```bash 
sudo sed -i 's/bookworm/trixie/g' /etc/apt/sources.list
sudo find /etc/apt/sources.list.d -type f -exec sed -i 's/bookworm/trixie/g' {} \;
```

Now make another full-upgrade

```bash 
sudo apt update 
sudo apt upgrade -y 
sudo apt full-upgrade -y
```

Now you need to reboot

```bash 
sudo reboot
```

Now you should remove all old packages from bookworm

```bash
sudo apt autoremove --purge 
sudo apt clean 
```

As simple as this.. as fast as your machine is :) 

