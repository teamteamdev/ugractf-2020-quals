#!/bin/sh -e

djgpp/bin/i586-pc-msdosdjgpp-gcc -Wall -O2 src/flag.c src/flappy.c -o flappy_pre.exe
djgpp/i586-pc-msdosdjgpp/bin/exe2coff flappy_pre.exe
cat csdpmi/bin/CWSDSTUB.EXE flappy_pre > flappy.exe
dosbox -conf dosbox.conf flappy.exe
