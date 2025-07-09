# vim

Keep it Stupid Simple

Install vim

```sh
# Debian based
sudo apt install vim
# Gentoo based
emerge -av vim
```

For Gentoo, Monkey use specific USE flags for vim ( you may wish to add or remove them )

```sh
equery u app-editors/vim # Check USE flags 
euse -p app-editors/vim -E acl crypt cscope terminal vim-pager
```

Create folder and configurations file

```sh
$ cd ~
$ mkdir .vim
$ cd .vim
$ touch vimrc
$ vim vimrc
```

Setup some default configurations and setup vim to use plugins.
```

Gentoo give you the option to install vim-plugins using portage, which it will automaticly update them and set them up.

You can check my own config [here](https://github.com/DaoExpression/vim)


