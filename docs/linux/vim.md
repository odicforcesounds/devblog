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

Monkey use specific USE flags for vim ( you may wish to add or remove them )

```sh
euse -p app-editors/vim -E X acl crypt gpm cscope python terminal vim-pager
```

Gentoo give you the option to install vim-plugins using portage, which it will automaticly update them and set them up.

```sh
filetype plugin indent on
syntax on
scriptencoding=utf-8
setglobal fileencoding=utf-8
set shortmess+=Ia
set ttimeout
set ttimeoutlen=0
set helpheight=30
set undolevels=3000
set history=10000
set cmdheight=1
set t_Co=256
set path+=**
set nomore
set nowrap
set wrapmargin=0
set equalalways
set sidescrolloff=999
set scrolloff=999
set encoding=utf8
set nocompatible
set novisualbell
set noerrorbells
set ignorecase
set smartcase
set foldenable
set foldcolumn=0
set foldmethod=marker
set foldmethod=indent
set foldlevel=0
set foldlevelstart=99
set expandtab
set softtabstop=2
set showtabline=2
set shiftwidth=2
set backspace =indent,eol,start
set display =lastline
set showmode
set showcmd
set incsearch
set hlsearch
set ttyfast
set lazyredraw
set splitbelow
set splitright
set cursorline
set wrapscan
set report=0
set synmaxcol=200
set list
set number
set hidden
set autoindent
set nobackup
set noswapfile
set history=100
set ruler
set matchtime=2
set tm=500
set nowrap
set nowb
set wildchar=<TAB>
set listchars=tab:»→,trail:␣
set secure
set novb
set scrolloff=5
set termwinsize=10x200
set wildignore=*.docx,*.jpg,*.png,*.gif,*.pdf,*.pyc,*.exe,*.flv,*.img,*.xlsx
au BufReadPost * if line("'\"") > 1 && line("'\"") <= line("$") | exe "normal! g'\"" | endif
au FileType text setlocal tw=120
au BufLeave ~/.vim/vimrc :source ~/.vim/vimrc
" prevent auto-comments
autocmd FileType * setlocal formatoptions-=c formatoptions-=r formatoptions-=o
" File Explorer
let g:netrw_browse_split=0
let g:netrw_winsize=15
let g:netrw_preview=1
let g:netrw_banner=0
let g:vetrw_sizestyle="H"
let g:netrw_liststyle=3
let g:netrw_altv=1
let g:netrw_alto=1
nnoremap <C-e> :Vexplore<CR> " Open Vertical Window - LEFT-SIDE
nnoremap <C-c> :hide<CR>
" splits shortcuts 
nnoremap <C-i> :split
nnoremap <C-l> :vsplit
" Tabs Control
nnoremap <C-t> :tabnew<CR> " Open New Tab File
nnoremap <C-n> :tabnext<CR> " Go to Next Tab File
nnoremap <C-p> :tabprevious<CR> " Go to Previous Tab File
" Save file
nnoremap <C-s> :w<CR> " Save file
" Colors
hi Directory ctermfg=cyan
hi ErrorMsg cterm=bold ctermfg=red ctermbg=black
hi LineNr ctermfg=darkblue ctermbg=NONE
hi StatusLine cterm=bold ctermfg=yellow ctermbg=black
hi StatusLineNC cterm=bold ctermfg=red ctermbg=black
hi Underlined cterm=underline ctermfg=gray ctermbg=black
hi Error cterm=bold ctermfg=red ctermbg=black
hi Title ctermfg=white ctermbg=black
hi Comment font='Monospace 16' ctermfg=darkcyan ctermbg=NONE
hi VertSplit ctermfg=grey ctermbg=NONE
hi Split ctermfg=grey ctermbg=NONE
hi SignColumn ctermfg=red ctermbg=NONE
hi CursorLineNr ctermfg=red ctermbg=NONE
hi Visual cterm=reverse ctermfg=black ctermbg=darkblue
hi NonText ctermfg=23 ctermbg=NONE
hi StatusLineTern ctermfg=yellow ctermbg=NONE
hi Terminal ctermfg=white ctermbg=NONE
hi WarningMsg ctermfg=red ctermbg=black
hi Search ctermfg=cyan ctermbg=black
hi IncSearch ctermfg=white ctermbg=black
" more colors to netrw
hi netrwCompress term=NONE cterm=NONE gui=NONE ctermfg=10   ctermbg=0
hi netrwData     term=NONE cterm=NONE gui=NONE ctermfg=9  ctermbg=0
hi netrwHdr      term=NONE cterm=NONE,italic gui=NONE
hi netrwLex      term=NONE cterm=NONE,italic gui=NONE 
hi netrwYacc     term=NONE cterm=NONE,italic gui=NONE 
hi netrwLib      term=NONE cterm=NONE gui=NONE ctermfg=14 
hi netrwObj      term=NONE cterm=NONE gui=NONE ctermfg=12 
hi netrwTilde    term=NONE cterm=NONE gui=NONE ctermfg=12 
hi netrwTmp      term=NONE cterm=NONE gui=NONE ctermfg=12 
hi netrwTags     term=NONE cterm=NONE gui=NONE ctermfg=12 
hi netrwSymLink  term=NONE cterm=NONE gui=NONE ctermfg=220 ctermbg=27

```

In most cases we don't need to use plugins.

In a while, check this site: http://zzapper.co.uk/vimtips.html
