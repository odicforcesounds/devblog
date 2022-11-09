# Cliente de IRC - irssi

- Fonte: irssi.org 

- Cores e Temas: https://irssi-import.github.io/themes/
- Modulos: https://irssi.org/modules/
- Scripts: https://scripts.irssi.org/

```bash
$ wget https://irssi-import.github.io/themes/c0ders.theme -o ~/.irssi/c0ders.theme
```

## Criar Certificado com o OpenSSL

```bash 
$ openssl req -x509 -new -newkey rsa:4096 -sha256 -days 1096 -nodes -out libera.pem -keyout libera.pem
```

## Ver o FingerPrint do Certificado 

```bash
$ openssl x509 -in libera.pem -noout -fingerprint -sha512 | awk -F= '{gsub(":",""); print tolower ($2)}'
```

## Adicionar o certificado ao servidor que nos iremos ligar 

```bash
$ mkdir ~/.irssi/certs 
$ mv libera.pem ~/.irssi/certs/libera.pem
```

## Connect to LiberaChat 

```sh 
/network add LiberaChat 
/server add -auto -network LiberaChat -tls -tls_verify irc.libera.chat 6697 
/network mofify -sasl_password 'mypassword' -sasl_mechanism EXTERNAL LiberaChat 
/server modify -tls_verify -tls_cert ~/.irssi/certs/libera.pem irc.libera.chat 6697
/connect LiberaChat
/msg nickserv identify password
/msg nickserv cert add FINGER_PRINT
/disconnect 
```

## Add tor address to /etc/tor/torrc 

MapAddress palladium.libera.chat libera75jm6of4wxpxt4aynol3xjmbtxgfyjpu34ss4d7r7q2v5zrpyd.onion

## Editar .irssi/config 

Mudar para o endereço de servidor para palladium.libera.chat 
e a porta para 6697 

## Test connect using tor and proxychains 

```sh
$ proxychains irssi 
```


