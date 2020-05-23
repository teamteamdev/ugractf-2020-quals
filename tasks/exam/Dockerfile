FROM ubuntu:20.04

RUN apt-get update && apt-get install -y build-essential ncurses-dev && rm -rf /var/lib/apt/lists/*
COPY history.cpp /root
RUN g++ -Wall -Werror -static /root/history.cpp -O2 -o /root/history -lformw -lncursesw -ltinfo && strip /root/history
