# Хай-тек I: Write-up

Полученный файл имеет расширение `.gz`, после расжатия архиватором gzip получаем файл `data.img`. Воспользуемся утилитой `file`:

```
$ file data.img
data.img: DOS/MBR boot sector, code offset 0x3c+2, OEM-ID "mkfs.fat", sectors/cluster 4, reserved sectors 4, root entries 512, Media descriptor 0xf8, sectors/FAT 128, sectors/track 32, heads 64, sectors 131072 (volumes > 32 MB), serial number 0xc5dae84c, unlabeled, FAT (16 bit)
```

Это — FAT. Примонтируем FAT:

```
# mkdir /media/task
# mount -t vfat -o ro,umask=000 
```

На Windows можно воспользоваться различными средствами для просмотра содержимого образа. На диске видим четыре директории, в одной из которых лежит скрытый файл `.agreement.txt.swp` — это бекап текстового редактора Vim. Восстановим его командой `vim -r .agreement.txt.swp`.

В месте электронной подписи видим base64 от флага.

Флаг: **ugra_vim_saves_the_world_e684b810bef535**.
