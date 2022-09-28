# Install nodejs from nodejs.org

## WAIT

use **NVM** to install only into your user $HOME 

You don't want NodeJS installed system-wide. ( if your machine is not a dedicated server )

```bash
apt install curl -y 
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.37.2/install.sh | bash
# Install the version of NodeJS You wish to use 
nvm install node # for the lastest non-long-term Version 
nvm install --lts # for the long-term-Support Version 
```

- Node is the V8 Engine that uses [JavaScript](./javascript.md) for Servers

- Have different options since it runs on server not in browser. ( there is no DOM object )

- We can use nodejs to speed up developing using the coc plugin with [vim](../linux/vim.md). 

- We use nodejs to build server-side websites ( back-end )

- We use nodejs to build **Desktop**, **iOS** and **Android** applications ( using Frameworks like **React-Native** )

- Nodejs comes with [npm](https://nodejs.com) which is used to install new packages

Normally, all configurations needed to access any script, is written in $HOME/.bashrc, but if not, just add this lines to the end of your $home/.bashrc file 

```bash 
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
```

Open new terminal or just ensure everything is working 

```bash 
source .bashrc
```

If You wish to use NodeJS Modules to develop or to make your Editor, responsive, as user, you can do it like: 

```sh
npm i -g eslint live-server
npm i -g typescript
```

Start developing: 

```bash 
cd code/project 
live-server 
```
