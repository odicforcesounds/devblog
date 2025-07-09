# Configure IPTables 

- Note: You should not change iptables rules often.. define what you need and configure it as it is! 

```
# Example: 

ip="/usr/sbin/iptables"

# Clear all IPTables rules

$ip -F 
$ip -X
$ip -Z 

# Normally we let (lo) interface to accept all traffic 

$ip -A INPUT -s 127.0.0.1/8 -j ACCEPT 
$ip -A OUTPUT -d 127.0.0.1/8 -j ACCEPT



```



