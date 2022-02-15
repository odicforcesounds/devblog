<h3> configure wifi </h3>

configure you wifi in new file

```sh
touch wifi.conf
vim wifi.conf
```

Then connect to your network

```sh
wpa_supplicant -B -c wifi.conf -i wlan0

dhclient -i wlan0
```
