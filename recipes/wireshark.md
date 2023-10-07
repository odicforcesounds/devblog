-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
https://www.wireshark.org/docs/dfref/ #Display Filter Reference
-----------------------------------------------------------1-----------------------------------------------1-------------------------------------------------------------------------
#Bing

Step-by-step instructions to decrypt TLS traffic from Chrome or Firefox in Wireshark:
https://wiki.wireshark.org/TLS.

How to decrypt TLS traffic in Wireshark
https://www.packetsafari.com/blog/2022/10/07/wireshark-decryption/
----------------------------------------------------------------------------------------------------------1-------------------------------------------------------------------------
#ChatGPT
Decrypting TLS 1.2 data using Wireshark requires capturing the encrypted network traffic and obtaining the necessary cryptographic information, including the (Pre)-Master-Secret. Here's a high-level overview of the process:

    Set up the environment:
        Install the latest version of Wireshark on your system.
        Configure your browser and Wireshark to capture the network traffic between the browser and the WCF service.

    Capture the network traffic:
        Open Wireshark and start capturing network traffic on the appropriate network interface.
        Reproduce the desired network connection between your browser and the WCF service, ensuring that the TLS 1.2 traffic is captured by Wireshark.

    Export the TLS session keys:
        Stop the network capture in Wireshark.
        Locate the TLS handshake packets in the captured traffic. These packets contain the (Pre)-Master-Secret required for decryption.
        Right-click on one of the TLS handshake packets and select "Follow" > "SSL" or "TLS" to view the details.
        In the SSL/TLS session details window, locate the "Pre-Master-Secret" or "Master-Secret" value. Right-click on it and choose "Export Packet Bytes."
        Save the exported packet bytes to a file, preferably with a ".key" extension.

    Configure Wireshark to decrypt the TLS traffic:
        Open the Wireshark application.
        Go to "Edit" > "Preferences" (or "Wireshark" > "Preferences" on macOS).
        In the Preferences window, select "Protocols" > "SSL."
        Click on "Browse" next to the "(Pre)-Master-Secret log filename" option.
        Browse and select the ".key" file containing the exported (Pre)-Master-Secret.
        Click "OK" to close the Preferences window.

    View the decrypted TLS traffic:
        Open the captured TLS 1.2 traffic in Wireshark.
        Wireshark will attempt to decrypt the TLS traffic using the provided (Pre)-Master-Secret.
        You should now see the decrypted TLS 1.2 data in the Wireshark capture, allowing you to inspect the exchanged messages between the browser and the WCF service.

Note: The (Pre)-Master-Secret method requires capturing the handshake packets and exporting the session keys during the capture. This means that you need to capture the traffic in real-time to obtain the necessary cryptographic information.

Keep in mind that decrypting TLS traffic should only be performed on your own network or with proper authorization. Decrypting traffic without proper permission may violate privacy and security guidelines.

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Bard

Here are the steps on how to decrypt TLS 1.2 data using Wireshark on a connection from the browser to the WCF service using the (Pre)-Master-Secret method:

    Start Wireshark and capture traffic from the browser to the WCF service.
    In Wireshark, go to Edit > Preferences > Protocols > TLS.
    In the (Pre)-Master-Secret log filename field, enter the path to a file where you want to save the (Pre)-Master-Secret values.
    Start the browser and connect to the WCF service.
    In Wireshark, filter for TLS traffic.
    Look for a packet that contains the (Pre)-Master-Secret value.
    Right-click on the packet and select Decode As > (Pre)-Master-Secret.
    The (Pre)-Master-Secret value will be displayed in the Decode As dialog box.
    You can now use the (Pre)-Master-Secret value to decrypt the TLS traffic.

Here are some additional tips for decrypting TLS 1.2 data using Wireshark:

    Make sure that you are using a recent version of Wireshark. Older versions of Wireshark may not be able to decrypt TLS 1.2 traffic.
    You may need to install the TLS dissector plugin for Wireshark. The TLS dissector plugin can be downloaded from the Wireshark website.
    If you are capturing traffic from a remote machine, you may need to use a proxy or a VPN to capture the traffic.
    Decrypting TLS 1.2 traffic may be illegal in some jurisdictions. Please check your local laws before attempting to decrypt TLS 1.2 traffic
    
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Bard

When capturing network traffic of a VM running in NAT mode with Wireshark, the IP address 10.0.2.2 will be used to represent the host machine. This is because the NAT mode in VirtualBox uses a private network that is isolated from the rest of the network. The IP address 10.0.2.2 is assigned to the host machine by VirtualBox and is used to communicate with the VM.

To capture network traffic of a VM running in NAT mode with Wireshark, you will need to do the following:

Start Wireshark and select the appropriate interface to capture traffic on.
In Wireshark, filter the traffic to only show traffic from the VM.
Start the VM and perform the actions that you want to capture traffic for.
When you are finished capturing traffic, stop Wireshark and save the capture file.
To filter the traffic to only show traffic from the VM, you can use the following filter:

Code snippet
ip.addr == 10.0.2.2
Use code with caution. Learn more
This filter will only show traffic that is sent to or from the IP address 10.0.2.2.

You can also use the following filter to show all traffic that is sent to or from the VM:

Code snippet
host 10.0.2.2
Use code with caution. Learn more
This filter will show all traffic that is sent to or from any IP address in the 10.0.2.0/24 subnet.

Once you have captured the traffic, you can use Wireshark to analyze it. Wireshark can be used to view the contents of the packets, as well as the headers of the packets. This information can be used to troubleshoot network problems, as well as to learn more about how the network works

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#ChatGPT

When capturing network traffic of a virtual machine (VM) running in NAT mode with Wireshark, the IP address 10.0.2.2 is significant as it represents the host machine's IP address from the perspective of the guest machine. Here's how it relates to capturing network traffic with Wireshark:

    NAT networking in VirtualBox: In NAT mode, VirtualBox sets up a virtual network interface on the guest machine that allows it to access the external network using the host machine's network connection. The host machine performs network address translation, allowing the guest machine to communicate with the outside world.

    Host-guest communication: The IP address 10.0.2.2 is automatically assigned to the host machine's virtual network interface within the guest machine. It serves as a gateway IP address that represents the host from the guest's perspective.

    Capturing traffic with Wireshark: To capture network traffic from the VM running in NAT mode using Wireshark, you need to select the appropriate network interface in Wireshark's capture options. Typically, this interface is associated with the NAT adapter in VirtualBox (e.g., "VirtualBox Host-Only Network" or "VMnet8").

    Set capture filter: Optionally, you can set a capture filter in Wireshark to focus on specific traffic of interest. For example, you can set a filter to capture traffic to or from the IP address 10.0.2.2:

    ip.addr == 10.0.2.2

    This capture filter will capture network packets involving communication to or from the host machine (from the guest machine's perspective).

    Generate traffic in the VM: Perform activities within the guest machine that generate the desired network traffic. This can include accessing websites, sending/receiving emails, or running specific applications.

    Capture and analyze traffic: Start the capture in Wireshark, allowing it to capture the network traffic on the selected interface. Analyze the captured packets to inspect the network communication between the guest machine and the external network, including any traffic involving the host machine's IP address (10.0.2.2).

By capturing network traffic in Wireshark with the appropriate network interface and using a capture filter that includes the IP address 10.0.2.2, you can focus on the communication between the guest machine and the host machine in a NAT environment. This enables you to monitor and analyze the network traffic generated by the guest machine, including its interaction with the host machine.
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#ChatGPT

In Wireshark, the time column in packet captures is typically displayed in a Unix timestamp format, which represents the number of seconds since the Unix epoch (January 1, 1970 at 00:00:00 UTC). To convert the time column to a human-readable format, you can follow these steps:

    In Wireshark, select the packet capture you want to view.

    Right-click on the "Time" column in the packet list pane.

    Select "Column Preferences" from the context menu.
    
    Columns > Type > List Down
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#ChatGPT
Explain :Frame 36708: 66 bytes on wire (528 bits), 66 bytes captured (528 bits) on interface \Device\NPF_{8448692C-9E4C-444E-AA93-5BD16BA7CDD2}, id 0

This appears to be a description of a network packet capture, which includes information about the packet's size and the interface it was captured on. Here's how the information in the description can be mapped to the OSI model:

    Physical Layer (Layer 1): The number of bits in the packet (528) and the interface it was captured on (\Device\NPF_{8448692C-9E4C-444E-AA93-5BD16BA7CDD2) both relate to the physical layer, which deals with the transmission of raw bits over a physical medium.

    Data Link Layer (Layer 2): The mention of a "Frame" in the description suggests that this is a data link layer packet. The size of the packet in bytes (66) indicates that it is a relatively small packet, which could suggest that it is a control packet (e.g., an acknowledgement or a request for retransmission).

    Network Layer (Layer 3) and higher: Without additional information, it's not possible to say which protocols are being used at the network layer (or higher layers, if present) in the packet capture. However, it's worth noting that the size of the packet (66 bytes) is well within the maximum transmission unit (MTU) for most network layer protocols, which is typically around 1500 bytes.

Overall, the description of the packet capture doesn't provide enough information to determine the specific protocol being used or the contents of the packet.
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#ChatGPT

Explain this according to OSI layer :Ethernet II, Src: HuaweiTe_dd:e8:7c (e0:24:7f:dd:e8:7c), Dst: VMware_be:3a:94 (00:50:56:be:3a:94)

The given information describes a data packet that was sent using the Ethernet II (also known as DIX) protocol. Ethernet II is a network protocol that operates at the data link layer (Layer 2) of the OSI (Open Systems Interconnection) model.

The packet's source address (Src) is "HuaweiTe_dd:e8:7c" (e0:24:7f:dd:e8:7c), which is the MAC (Media Access Control) address of the device that originated the packet. The MAC address is a unique identifier assigned to each network interface controller (NIC) of a device.

The destination address (Dst) is "VMware_be:3a:94" (00:50:56:be:3a:94), which is the MAC address of the device that the packet is intended for. The MAC address is used at the data link layer to direct packets to the correct destination.

Therefore, the information given pertains to Layer 2 (Data Link Layer) of the OSI model, specifically the Ethernet II protocol.
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#ChatGPT

In Wireshark, the "coloring rule name TCP SYN/FIN" refers to a display filter that highlights packets in the capture that have both the SYN and FIN flags set in the TCP header. The SYN and FIN flags are used by the TCP protocol to establish and terminate connections, respectively.

When a TCP connection is established, the client sends a packet with the SYN flag set to initiate the connection, and the server responds with a packet with both the SYN and ACK flags set to acknowledge the request and initiate the connection. When a connection is terminated, the sender sends a packet with the FIN flag set to indicate that it has finished sending data, and the receiver sends a packet with both the FIN and ACK flags set to confirm receipt of the FIN packet and indicate that it has finished receiving data.

By highlighting packets with both the SYN and FIN flags set, the "coloring rule name TCP SYN/FIN" helps to identify potentially suspicious network activity, such as a TCP SYN/FIN scan, where an attacker sends packets with the SYN and FIN flags set to attempt to probe for open ports or vulnerable systems. The coloring rule can be useful in detecting such attacks and other anomalies in network traffic.

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
eth.addr 	Traffic to or from an ethernet address
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
wlan.addr 	Hardware address [Ethernet or MAC address]
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
arp.src.proto_ipv4 	Sender IP in ARP packets
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
tcp.analysis.ack_rtt 	Round-trip time

#The TCP retransmission mechanism ensures that data is reliably sent from end to end
tcp.analysis.retransmission 	#Display all the retransmissions,packet loss has occurred on the network somewhere between client and server
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#wireshark version 3.4.9, after downloading&configuring maxmind databases
ip and not ip.geoip.country == "United States"  #Exclude U.S.-based traffic
ip.geoip.dst_city == "Dublin" #Destination City [IPv4] 
ip.geoip.city == "Dublin" #Source or Destination City [IPv4]  
ip.geoip.dst_country == "Ireland"
ip.geoip.dst_country_iso == "IE"
!ip.geoip.country == "United States" #All Destination Countries Except United States
not ip.geoip.country == "United States" #All Destination Countries Except United States:  
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#wireshark version 3.4.9
ip.addr == 10.43.54.0/24 
ip.dst == 10.43.54.0/24 #destinatioon ip address
ip.src == 10.43.54.0/24
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
eth.dst == 00:0C:CC:76:4E:07 #source mac filter
eth.src == 00:0C:CC:76:4E:07 #destination mac filter
ether host 00:18:0a:aa:bb:cc #a specific mac. This will not work on interfaces where traffic has been NATed like NAT mode SSID or an Internet interface

bootp.hw.mac_addr == 00:0C:29:D5:AA:AA
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Protocol filter
tcp - will only display TCP packets
udp - will only display UDP packets
icmp - will only display ICMP (ping) packets
dhcp - will display DHCP packets (if you are using an old version of Wireshark you'll need to use bootp)
dns - will display DNS packets
telnet  - will telnet DNS packets
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#DORA - Discover, Offer, Request, and Ack
#Display Filter Reference: Dynamic Host Configuration Protocol https://www.wireshark.org/docs/dfref/d/dhcp.html 

dhcp and ip.addr == 10.43.54.0/24 #only dhcp 
dhcp.hw.mac_addr == a4:83:e7:c9:37:cd #find DORA - Discover, Offer, Request, and Ack.The DORA all has the same ID
(dhcp and ip.addr == 10.43.54.0/24) and ip.addr == 10.43.54.99 # DHCP MMC - Client IP Address
(dhcp and ip.addr == 10.43.54.0/24) and dhcp.hw.mac_addr == a4:83:e7:c9:37:cd # DHCP MMC - Unique ID (Client MAC Address)
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
tcp.port == 80 - this will display un-encrypted TCP traffic on port 80. 
tcp.port == 443 - this will only show encrypted TCP traffic using port 443. 
udp.port == 53 - another way of specifying DNS traffic, this will filter off of DNS's use of UDP port 53. 
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#https://www.wireshark.org/docs/dfref/d/dns.html
#https://www.wireshark.org/docs/dfref/d/dnsserver.html

(tcp.dstport == 53) && (dns.flags.response == 0) && (dns.qry.type == 0x00fc) #DNS Zone Transfer request 
(tcp.srcport == 53) && (dns.flags.response == 1) && (dns.qry.type == 0x00fc) #DNS Zone Transfer response
dns.qry.type in {251 252} or dns.flags.opcode eq 4 #DNS Zone Transfer



#UDP or TCP Stream
udp.stream eq ${udp.stream}
tcp.stream eq ${tcp.stream}

#Retransmit the query with the same transaction ID to their primary server
#Retransmit the query with the same transaction ID to their secondary (or ternary) server
#If retransmits the query to either their secondary or ternary servers, the UDP stream number changes.The transaction ID does not.
dns.id eq ${dns.id} 
dns.id == 0xff0b #Transaction ID

#nslookup yahoo.com 193.247.121.196 #dns query via dns server(193.247.121.196),optional
dns.resp.name == yahoo.com 
dns.resp.name == yahoo.com  and dns.time > 0.01

dns.time > 0.5 #0.5 seconds 500 miliseconds
dns.time > 1 # 1 sec
dns.time > .6 # greater than 600 miliseconds

dns and dns.qry.name == "microsoft.com" #filter based on the queried domain name
dns.qry.name contains mail.yahoo.com and dns
 
#https://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml
dns.qry.type == 15 #filter MX queries

DNS pointer(PTR) query/response
dns.qry.type == 12
udp.port == 53
port 53 #Capture only DNS (port 53) traffic
port not 53 and not arp #Capture except all ARP and DNS traffic
!dns.response_in and dns.flags.response == 0 and dns # the lack of a recorded reply (!dns.response_in) combined with only looking for DNS queries (dns.flags.response == 0) that are only UDP port 53 (dns)
dns.flags.response == 0 # only DNS queries
dns.flags.response eq 1 # only DNS response queries

#https://datatracker.ietf.org/doc/html/rfc6895 RFC 6895 Domain Name System (DNS) IANA Considerations
dns.flags.rcode != 0 or (dns.flags.response eq 1 and dns.qry.type eq 28 and !dns.aaaa) #DNS Errors
dns.flags.rcode == 3 #NXDomain  Non-Existent Domain
((dns.flags.rcode == 3) && !(dns.qry.name contains ".local") && !(dns.qry.name contains ".svc") && !(dns.qry.name contains ".cluster"))
(dns.flags.rcode == 0) && (dns.qry.name == "microsoft.com") #No Error ,nslookup microsoft.com 193.247.121.196

dns.flags.rcode != 0 or (dns.flags.response eq 1 and dns.qry.type eq 28 and !dns.aaaa)
dns.flags.rcode eq 0 and dns.time gt .1 #Slow Responses

dns.flags.rcode > 0 #finding DNS errors
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Ping sweep
icmp.type == 8 || icmp.type == 0
ICMP Type 8 = ECHO Request
ICMP Type 0 = ECHO Reply
icmp || icmpv6

(icmp.type==3) && (icmp.code==1) 

“icmp.type==8 and not icmp.resp_in“ #filter for all ICMP echo request packets where the “response in” field does not exist, and find all unanswered pings
“icmp.type==8 and icmp.resp_not_found“ #no response was seen
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

tcp.dstport == 25 #Wireshark Filter Destination Port
tcp.port in {443 4430..4434}

tcp.flags.reset == 1 && tcp.flags.ack == 1 && tcp.seq == 1 && tcp.ack == 1 #connection refusal ACK scan

http.request
http.request.method == GET
http.request.method == POST #Wireshark Filter HTTP POST
http.request.method == POST && frame contains "login" #Wireshark Filter HTTP POST

#Capture HTTP GET requests
port 80 and tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x47455420 #looks for the bytes 'G', 'E', 'T', and ' ' (hex values 47, 45, 54, and 20) just after the TCP header. "tcp[12:1] & 0xf0) >> 2"

ip.addr == 10.43.54.65
ip.addr == 10.92.182.6 or ip.addr == 172.16.7.7 - is going to display both 10.92.182.6 as well as 172.16.7.7
ip.addr== 192.168.12.160 and ip.addr==192.168.12.161 #Filter packets between two devices in a capture, menu -> statistics -> conversations
ip.addr >= 10.80.211.140 and ip.addr <= 10.80.211.142
ip.addr == 10.92.182.6 and dns - will only show the host 10.92.182.6 and it's DNS traffic. 
(ip.addr == 172.16.7.42 or ip.addr == 172.16.7.7) and dns - is going to show dns traffic for two IPs 172.16.7.42 OR 172.16.7.7
(ip.addr == 172.16.7.42 and dns) or (172.16.7.7 and icmp) - here the parentheses are being used to combine two completely different filters. DNS traffic for 172.16.7.42 as well as icmp traffic for 172.16.7.7. 
not ip.addr == 172.16.7.7 - is going to exclude all traffic that has an IP of 172.16.7.7
ip.dst == 10.43.54.65
ip.src == 10.43.54.65

#tcp 3 way handshake, https://www.mdpi.com/applsci/applsci-06-00358/article_deploy/html/images/applsci-06-00358-g001.png
ip.addr== 192.168.12.160 and ip.addr==192.168.12.161 and (tcp.flags == 0x0012) #looks for TCP flags set,displays the ones which have both SYN and ACK set.
ip.addr== 192.168.12.160 and ip.addr==192.168.12.161 and and (tcp.seq==0 or (tcp.seq==1 and tcp.ack == 1 and tcp.nxtseq==1))

#analyze - conversation filter - TCP
“tcp.flags.syn==1 or (tcp.seq==1 and tcp.ack==1 and tcp.len==0 and tcp.analysis.initial_rtt)” #show the handshake packets of any conversation,

Edit > Preferences > Protocols > TCP > Relative sequence numbers #get the actual TCP sequence number

Wireshark Filter SYN
tcp.flags.syn == 1
tcp.flags.syn == 1 && tcp.flags.ack == 0
SYN/ACK packets(bitwise filter)
tcp.flags & 0x12
tcp.flags.syn == 1 && tcp.flags.ack == 0 && tcp.ack == 0

TLS handshake
tls.record.content_type == 22
only TLS traffice
tls
client Hello
tls.handshake.type == 1
server Hello
tls.handshake.type == 2
connection close
tls.record.content_type == 21
tls.handshake.extensions_server_name contains "badsite"
#When the timeout occurs, the client usually sends an RST to the server to filter out the packets with the handshake timeout. 
(tcp.flags.reset eq 1) and (tcp.flags.ack eq 0)
#Filter out packets that are slow to respond to SYNACK during the server handshake
tcp.flags eq 0x012 && tcp.time_delta gt 0.0001

frame contains "tls"

net 192.168.0.0/24 #Capture traffic to or from a range of IP addresses
dst net 192.168.0.0/24 #Capture traffic to a range of IP addresses
src net 192.168.0.0/24
src net 192.168.0.0 mask 255.255.255.0

host 172.18.5.4 #Capture only traffic to or from IP address 172.18.5.4
host www.example.com and not (port 80 or port 25) #Capture non-HTTP and non-SMTP traffic on your server (both are equivalent)
host www.example.com and not port 80 and not port 25
host 8.8.8.8 # capture traffic going to the Google DNS server 8.8.8.8. 

(tcp[0:2] > 1500 and tcp[0:2] < 1550) or (tcp[2:2] > 1500 and tcp[2:2] < 1550) #Capture traffic within a range of ports
tcp portrange 1501-1549

ether proto 0x888e #Capture only Ethernet type EAPOL
not ether dst 01:80:c2:00:00:0e #Reject ethernet frames towards the Link Layer Discovery Protocol Multicast group
not broadcast and not multicast

ip #Capture only IPv4 traffic,get rid of lower layer protocols like ARP and STP

dst port 135 and tcp port 135 and ip[2:2]==48 #Blaster worm
#Welchia worm
#looks for an icmp echo request that is 92 bytes long and has an icmp payload that begins with 4 bytes of A's (hex)
#the signature of the welchia worm just before it tries to compromise a system
icmp[icmptype]==icmp-echo and ip[2:2]==92 and icmp[8:4]==0xAAAAAAAA 
# worm query
#looks for SYN packets originating from a local network on those specific ports,contacting other hosts on ports 135, 445, or 1433
dst port 135 or dst port 445 or dst port 1433  and tcp[tcpflags] & (tcp-syn) != 0 and tcp[tcpflags] & (tcp-ack) = 0 and src net 192.168.0.0/24

#Heartbleed Exploit
tcp src port 443 and (tcp[((tcp[12] & 0xF0) >> 4 ) * 4] = 0x18) and (tcp[((tcp[12] & 0xF0) >> 4 ) * 4 + 1] = 0x03) and (tcp[((tcp[12] & 0xF0) >> 4 ) * 4 + 2] < 0x04) and ((ip[2:2] - 4 * (ip[0] & 0x0F)  - 4 * ((tcp[12] & 0xF0) >> 4) > 69))
------------------------------------------------IPv6 basecamp------------------------------------------------
dst host ff02::1 #Capture IPv6 "all nodes" ,find rogue RAs
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Menu-View-Packet Bytes #The “Packet Bytes” pane
canonical hex dump of the packet data
Each line contains the data offset(left), bytes interpreted as sixteen hexadecimal(middle), and bytes interpreted a sixteen ASCII (right). Non-printable bytes are replaced with a period (“.”).

offset(left) (hexadecimal) beginning of the frame
0010 0x10 16
0020 0x20 32
0030 0x30 48

left middle                                           right
0020 20 21 22 22 24 25 26 27  28 29 2A 2B 2C 2D 2E 2F 
0030 30 31 32 33 34 35 36 37  38 39 3A 3B 3C 3D 3E 3F  

3F(hexadeciaml)=63(decimal) -> 63rd byte 

"X" in ascii = 78 in hexadecimal

converter hexadecimal,decimal,byte etc.
https://www.rapidtables.com/convert/number/hex-to-decimal.html
converter table
https://circuitglobe.com/wp-content/uploads/2016/09/hexadecimal-to-binary-conversion-examples-3.jpg
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Menu-View-Coloring Rules-Import #https://gitlab.com/wireshark/wireshark/-/wikis/ColoringRules
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Tor
tcp.port == 9001 or tcp.port == 9030 or  tcp.port == 9150

#RawCap
RawCap.exe -q 127.0.0.1 - | Wireshark.exe -i - -k #Streaming PCAP to Wireshark
#write the PCAP data to a named pipe, and then let Wireshark "sniff" packets from that named pipe
RawCap.exe 127.0.0.1 \\.\pipe\RawCap #write PCAP data to a named pipe called "RawCap"
Wireshark-Capture-Options-Manage Interfaces-Pipes- "+" button -Name the pipe "\\.\pipe\RawCap" 
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#https://www.wireshark.org/docs/dfref/x/x509ce.html
SL.handshake.type==1 SSL  Client  Hello  requests

#https://www.wireshark.org/docs/dfref/x/x509sat.html
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#LDAP  https://wiki.wireshark.org/LDAP.md
tcp port 389  #Capture LDAP traffic over the default port (389)
ldap #Show only the LDAP based traffic
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------