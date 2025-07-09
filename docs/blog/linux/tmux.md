Using tmux

edit ~/.tmux.conf and add this lines: 
```sh
set -g default-terminal "screen-256color"
set -g history-limit 20000
set -g buffer-limit 20
set -sg escape-time 0
set -g display-time 1500
set -g remain-on-exit off
set -g repeat-time 300
setw -g allow-rename on
setw -g automatic-rename on
unbind C-b
set -g prefix C-a
set -g set-titles on
set -g base-index 1 
setw -g pane-base-index 1
set -g visual-silence on
set -g visual-activity off
set -g visual-bell off
set -g mode-keys vi 
set -g status on
set -g status-interval 5
set -g status-position top
setw -g window-status-format "#[fg=white]#[bg=black] *#I #[bg=black]#[fg=lightgreen] #W "
setw -g window-status-current-format "#[bg=black]#[fg=yellow] *#I #[bg=black]#[fg=cyan] [#W] "
bind C-r source-file ~/.tmux.conf

```

Now use normal key-bindings

- Ctrl+a c ( new tab )
- Ctrl+a " ( horizontal split )
- Ctrl+a % ( vertical split )
- Ctrl+a x ( kill/close window )
- Ctrl+a d ( detach/hide tmux )
- Ctrl+a 2 ( each number represents each tab )
- Ctrl+a >^< ( use arrow-keys to change from splited windows ) or lkjh

Remember to re-open tmux sessions

```bash 
tmux a 
```

Enjoy simplicity 

