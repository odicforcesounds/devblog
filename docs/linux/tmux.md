Using tmux

edit ~/.tmux.conf and add this lines: 
```sh
unbind C-b
set-option -g prefix C-a
bind-key C-a send-prefix
setw -g window-status-format "#[fg=white]#[bg=black] *#I #[bg=black]#[fg=lightgreen] #W "
setw -g window-status-current-format "#[bg=black]#[fg=yellow] *#I #[bg=black]#[fg=cyan] [#W] "
set-option -g status-position top

setw  -g mode-keys vi
set-option -g default-shell /bin/bash
set-option -g set-titles on

set -q -g urf8 on
set -g base-index 1
set -g pane-base-index 1
set -g visual-activity off
set -g visual-bell off
set -g visual-silence off
set -g bell-action none
setw -g monitor-activity off

set -g status-bg black
set -g status-left ''
set -g status-right-length 60
set -g status-interval 60
setw -g status on

bind r source-file ~/.tmux.conf
```

Now use normal key-bindings

- Ctrl+a c ( new tab )
- Ctrl+a " ( horizontal split )
- Ctrl+a % ( vertical split )
- Ctrl+a x ( kill/close window )
- Ctrl+a d ( detach/hide tmux )

Remember to open tmux sessions

```bash 
tmux a 
```

Enjoy simplicity 

