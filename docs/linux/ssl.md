# Open SSL 
# SSL Certificate - How to generate

- Save Certificate Password into ENV: 

```sh 
export MYPASS='MonkeyFunkyPassword'
```

- Generate New SSL Certificate

```
openssl req -new -passout env:MYPASS -subj "/CN=sample.myhost.com" -out newcsr.csr -sha512 -newkey rsa:4096
```

- Move certicate files into application directory

```
mv *.crt *.key /etc/vpn/
```

more examples

```
mv *.crt *.key /var/www/
```

... Then edit your configuration application file to point the Certificates to the correct path. 



