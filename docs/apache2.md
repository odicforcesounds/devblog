# Apache2

I really love the **old** [Apache](https://httpd.apache.org/), which was published in the same year I start to use Internet. Those awesome times that I met the best Social-Network in the world called **IRC**. No Pictures, total freedom to create your own name, conversations are about specific topics and no censurship, in the aspect of what each one believe. I still use this **awesome** Social-Network for some technical help or talk. **Freenode** die but **Libera** come to play and to say: "We are here because we Love FREEDOM" :) 

They offer this way to be annonymous and you can even add Tor proxy or VPNs to be more hidden. I could kiss them all, while that sound a bit gay.. anyway.. in this aspect of how I wish to tell them how much I love their work, I can be a bit gay for them. LoL 

Anyway, this article is about Apache, not about the amazing [lists](https://github.com/davisonio/awesome-irc) of IRC servers. 

I wish to share some configurations of how to setup Apache. First you install it. I will assume you know to do that, or using a package-manager or compiling it fromt the source. 

```bash
# /etc/apache2/apache2.conf 
ServerRoot "/etc/apache2"
DefaultRunTimeDir ${APACHE_RUN_DIR}
PidFile ${APACHE_PID_FILE}
Timeout 300
KeepAlive on 
MaxKeepAliveRequests 100 
KeepAliveTimeout 5 
User ${APACHE_RUN_USER}
Group ${APACHE_RUN_GROUP}
HostnameLookups off 
ErrorLog ${APACHE_LOG_DIR}/error.log 
LogLevel warn 
Include ports.conf 
IncludeOptional mods-enabled/*.load 
IncludeOptional mods-enabled/*.conf 
IncludeOptional conf-enabled/*.conf
IncludeOptional sites-enabled/*.conf 
Servername ${IP_OF_MY_SERVER} 
AccessFileName .htaccess
```

Directory directives are similar between them

```bash 
Options Indexes FollowSymLinks
AllowOverride All 
Require all granted
```

One of the best features Apache have is the way it manage **Reverse Proxy**. 

What ever the port your application is using, you can limit to your host only and link it to one single path of your site, with the name of your choice: 

`localhost:80/secret/app/for/those/who/know/what/secret/folders/are/for/` 

and your application can be running at `localhost:8080` 

this is what I love most. 

Anyway, just use **CertBot** to create a **LetsEncrypt** Certificate and add all details that you may wish to setup. here is an example: 

```bash 
# /etc/apache2/sites-enabled/myAwesomeWebSite.org 
Servername myAwesomeWebSite.org 
ServerAdmin root@localhost 
DocumentRoot /var/www/html 
LogLevel info ssl:warn 
Options -ExecCGI +MultiViews +SymLinksIfOwnerMatch
RemoveHandler .cgi, .php, .php3, .php4, .php5, .pl, .py, .pyc 
SSLEngine on 
SSLCertificateFile /etc/LetsEncrypt/live/myAwesomeWebSite/fullchain.pem 
SSLCertificateKeyFile /etc/LetsEncrypt/live/myAwesomeWebSite/privkey.pem 
Include /etc/LetsEncrypt/options-ssl-apache.conf 
```

... Oops, I didn't use the Proxy Options :) 

Well, that is the moment you should investigate in Apache-website. 

Or, join Libera IRC servers and join Apache #channel to get some help. 

Enjoy the Show! 
