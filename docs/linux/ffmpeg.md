# FFMPEG 

Install package 

```
# apt install ffmpeg 
emerge -av ffmpeg 
```
- Convert any to any 

```
ffmpeg -i file.mp4 file.mp3
```

- Record monitor 2 desktop

``` 
ffmpeg -y -video_size 1920x1080 -framerate 30 -f x11grab -i :0.0 -vsync 0 -c:v prores -f alsa -ac 2 -i default result.mkv
```

A player is recommended

Try MPlayer or MPV to play video files and listen to online radios

MPV can be used to listen youtube video-audios. 


