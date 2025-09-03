# NChat 

- In reference to: https://github.com/d99kris/nchat/

I really like to use this TUI application to be online on Whatsapp. 

Is possible to be on Telegram, but I don't use it. 

Here is some tips: 

Since you can use another GNU/Linux distribution than the ones selected in the script, you can always install it by hand. 

Each Distro have their own package name, so be careful with the dependencies. 

After all set, install this application: 

```bash 
cd nchat 
mkdir build 
cd build 
cmake ../ 
make 
``` 

Wait, you need to install it. If your user is part of 'sudo' group is easy. Else you need to 'su -l' in. 

```bash 
sudo make install 
```

Sadly most friends use Whatsapp, not IRC, which I really prefere. 

