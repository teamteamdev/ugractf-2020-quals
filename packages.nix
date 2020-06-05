{
  binPackages = pkgs: with pkgs; [
    coreutils
    bash
    gnused
    zip
    tcpreplay
    (texlive.combine { inherit (texlive) scheme-small collection-langcyrillic; })
    mtools
    dosfstools
    imagemagick
    inkscape
    socat
    gcc
    patchelf
    ffmpeg_4
    openscad
    mongodb
    docker
    docker-compose
  ];

  pythonPackages = self: with self; [
    flask
    pillow
    qrcode
    pycryptodome
    uvloop
    aiohttp
    aiohttp-jinja2
    aiohttp-session
    gunicorn
    numpy
    aiosqlite
    telethon
    XlsxWriter
    pymp4
    motor
    pysocks
  ];
}
