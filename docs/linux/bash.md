# Bash and shell scripts

Use scripts to automate your terminal use-cases

- Check Your Personal Public and Local IP Address  

```Bash
#!/bin/bash 
# check your personal public ip address 
# apt install bind9-dnstools bind9-utils 
ipc=$(ip a show wlan0 | grep "inet " | cut -b 10-23) 
ipb=$(dig +short myip.opendns.com @resolver1.opendns.com)
echo "Your Private IP address is:" $ipc
echo "Your Public IP address is:" $ipb
```

- Other example to automate wifi manual connection using [WPA Supplicant](./wpa_supplicant.md)

```bash 
#!/bin/bash
WIFI_CARD="wlan0"
WIFI_CONFIG="/etc/wpa_supplicant/wpa_supplicant.conf"
# kill -9 $(pidof wpa_supplicant)
# kill -9 $(pidof dhclient)
sleep 2
echo "wpa and dhclient process were killed"
sleep 1 
echo "starting connection using dhclient and wpa_supplicant"
wpa_supplicant -B -c $WIFI_CONFIG -i $WIFI_CARD
sleep 2
dhclient -v $WIFI_CARD
```

- Ohter example to Record your desktop using **FFMPEG** with ALSA 

```bash 
#!/bin/sh
ffmpeg -video_size 1920x1080 -framerate 25 -f x11grab -i :0.0 -f alsa -ac 2 -i hw:0 output.mkv
``` 

