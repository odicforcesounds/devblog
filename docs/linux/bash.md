# Bash and shell scripts

Use scripts to automate your terminal use-cases 

```Bash
#!/bin/bash 
# check your personal public ip address 
# apt install bind9-dnstools bind9-utils 
ipc=$(ip a show wlan0 | grep "inet " | cut -b 10-23) 
ipb=$(dig +short myip.opendns.com @resolver1.opendns.com)
echo "Your Private IP address is:" $ipc
echo "Your Public IP address is:" $ipb
```

Other example 

```bash 
#!/bin/bash
WIFI_CARD="wlp2s0"
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



