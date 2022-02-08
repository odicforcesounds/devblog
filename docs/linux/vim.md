# vim

Keep it Stupid Simple

Install vim

```sh
# Debian based
$ sudo apt install vim
# Gentoo based
$ sudo emerge -av vim
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

```sh
set nocompatible
set encoding=UTF-8
set fileencodings=utf-8,latin1
set termencoding=utf-8
set number
set history=999
set undolevels=999
set autoread
set nobackup
set softtabstop=2
set shiftwidth=2
set smarttab
set nowritebackup
set tabstop=2
set gdefault
set magic
set hlsearch
set incsearch
set ignorecase smartcase
set backspace=indent,eol,start
set esckeys
set nostartofline
set timeoutlen=500
set ttimeoutlen=100
set title
set splitbelow splitright
set scrolloff=7
set sidescroll=1
set hls
set novb
set tabstop=2
set showtabline=2
set cursorline
set secure
set showmode
set showmatch
set nohidden
set ttyfast
set noerrorbells
set report=0
set nowb
set noswapfile
set wildmenu
set wildchar=<TAB>
set wildmode=list:longest
set wildignore+=*/.git/*,*/.svn/*,*/node_modules/*
set wildignore+=*.DS_STORE,*.db,node_modules/**,*.jpg,*.png,*.jpeg,*.gif
set foldmethod=manual
set foldnestmax=3
set nofoldenable
set copyindent
set softtabstop=2
set smarttab
set expandtab
set visualbell
set wrap
set textwidth=120
set formatoptions=qrn1
set formatoptions-=o
set nomodeline
set pastetoggle=<leader>p
set selection=inclusive
set t_vb=
set tm=500
set showcmd
set matchtime=2
```

List or Recommended Plugins for Vim:

| Editor | Plugin        | Objective        | Github |
| ------ | ------------- | ---------------- | ------ |
| vim    | Fugitive      | Manage Git       | .....  |
| vim    | NerdTree      | Manage Files     | ....   |
| vim    | NerdCommenter | Comment lines    | ....   |
| vim    | tmuxline      | Tmux Integration | ....   |
| vim    | CoC           | Auto-complete    | ....   |
