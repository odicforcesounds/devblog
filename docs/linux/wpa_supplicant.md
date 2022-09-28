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

Then connect to your network

```sh
wpa_supplicant -B -c /etc/wpa_supplicant/wpa_supplicant.conf -i wlan0
sleep 3 
dhclient -v wlan0
```
