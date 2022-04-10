# Bash and shell scripts

```sh
apt install golang
go install github.com/zquestz/s 
echo "PATH=~/go/bin" >> .bashrc
mkdir bin
touch bin/ddrs.sh
echo "#!/bin/bash" >> bin/ddrs.sh
echo "echo 'Insert keyword to search'" >> bin/ddrs.sh
echo "read NAME" >> bin/ddrs.sh
echo "lynx $(s -p duckduckgo $NAME -o)" >> bin/ddrs.sh
echo "Done!"
chmod +x bin/ddrs.sh
```
