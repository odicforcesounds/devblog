# Configure wifi 

- Install wpa_supplicant 

```bash 
apt install wpasupplicant --no-install-recommends -y 
```

- Add new configuration to new file or at 

```bash
# /etc/wpa_supplicant/wpa_supplicant.conf 
network={
        ssid="our-SSID"
        scan_ssid=1
        key_mgmt=WPA-PSK
        psk="M0Nk3Y"
}
``` 

Then "say hi so you can be recognized" to our-Wifi-Router

```sh
wpa_supplicant -B -c /etc/wpa_supplicant/wpa_supplicant.conf -i wlan0
```

Connect using DHCP
```bash 
dhclient -v wlan0
```

Test Connection

```bash 
ping -c google.com 
```

