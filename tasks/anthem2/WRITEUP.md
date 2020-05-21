# Гимн года: продолжение: Write-up

```
-c:v copy

ffmpeg -skip_estimate_duration_from_pts 1 -fflags +genpts+igndts -vsync 0 -r 25 -i anthem2-copied.mp4 -vf setpts=PREV_OUTPTS+1 frame%04d.jpg
```

Флаг: **ugra_like_and_subscribe_adacddfeaaba**.
