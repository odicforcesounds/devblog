# DNS stuff

- Check public IP 

```
# Install necessary tools

emerge -av bind-tools

#!/bin/bash
iip=$(ip a show eth0 | grep "inet " | cut -b 10-23)
oip=$(dig +short myip.opendns.com @resolver1.opendns.com)
echo "Your private IP address is: " iip # Internet IP 
echo "Your public IP address is: " $oip # Outside IP
```



