#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import aiohttp.web as web
import hmac
import os
import socket
import random
import re
import sys
import time

BASE_DIR = os.path.dirname(__file__)

PREFIX = "ugra_did_you_ever_feel_that_clean_"
SECRET2 = b"metal-chimney-fork-unleash-vertigo"
SALT2_SIZE = 12


def get_flag(token):
    return PREFIX + hmac.new(SECRET2, token.encode(), 'sha256').hexdigest()[:SALT2_SIZE]


SLICES = 20
SECONDS = 2
async def send_chunk(response, size):
    for _ in range(SLICES):
        await response.write(b"\x00" * (size // SLICES))
        await asyncio.sleep(SECONDS / SLICES)


def build_app():
    app = web.Application()
    app["atimes"] = {}
    routes = web.RouteTableDef()

    @routes.get('/{token}/')
    async def root(request):
        return web.Response(text='Попробуйте скачать <a href="dev/zero">/dev/zero</a>.',
                            headers={"Content-type": "text/html; charset=utf-8"}, status=404)

    @routes.get('/{token}/dev/zero')
    async def devzero(request):
        token = request.match_info["token"]
        flag = get_flag(token)

        if "Range" in request.headers:
            return web.Response(text="HTTP/1.1 416 Да какая разница, всё равно там одни нули", status=416)

        response = web.StreamResponse()
        response.content_type = "appication/octet-stream"
        await response.prepare(request)

        for byte in flag.encode():
            for bit in [bool((1 << i) & byte) for i in range(7, -1, -1)]:
                if bit:
                    await send_chunk(response, 10000)
                else:
                    await send_chunk(response, 2000)

        while True:
            await send_chunk(response, 5000)

        return response

    app.add_routes(routes)
    return app


def start():
    app = build_app()

    if os.environ.get('DEBUG') == 'F':
        web.run_app(app, host='0.0.0.0', port=31337)
    else:
        sock_path = os.path.join(sys.argv[1], "devzero.sock")
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            os.unlink(sock_path)
        except FileNotFoundError:
            pass
        s.bind(sock_path)
        os.chmod(sock_path, 0o666)
        web.run_app(app, sock=s)


if __name__ == '__main__':
    start()
