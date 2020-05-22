# Гимн года II: Write-up

```
-c:v copy

ffmpeg -vsync 0 -i anthem2-c.mp4 -vf setpts=PREV_OUTPTS+1 frame%04d.jpg

можно просто -r 1 у инпута
```

Флаг: **ugra_like_and_subscribe_adacddfeaaba**.
