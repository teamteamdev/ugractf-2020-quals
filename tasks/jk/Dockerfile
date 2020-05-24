FROM ubuntu:20.04

RUN echo "deb http://us.archive.ubuntu.com/ubuntu/ focal multiverse" >> /etc/apt/source.list
RUN echo "deb-src http://us.archive.ubuntu.com/ubuntu/ focal multiverse">> /etc/apt/source.list
RUN echo "deb http://us.archive.ubuntu.com/ubuntu/ focal-updates multiverse" >> /etc/apt/source.list
RUN echo "deb-src http://us.archive.ubuntu.com/ubuntu/ focal-updates multiverse" >> /etc/apt/source.list

RUN apt update && apt install -y rar=2:5.5.0-1build1 && rm -rf /var/lib/apt/lists/*
COPY unrar /root
COPY rar.sh /root
RUN chmod +x /root/rar.sh
WORKDIR /root
RUN ./rar.sh
