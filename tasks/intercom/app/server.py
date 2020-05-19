#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import aiohttp
import aiohttp.web as web
import hmac
import os
import re
import sys

BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, 'static')

PREFIX = "ugra_pati_na_hate_"
SECRET1 = b"untracked-files-recent-commits"
SALT1_SIZE = 16
SECRET2 = b"file-edit-options-buffers-tools-python-help"
SALT2_SIZE = 12

FACTORY_CODES = ["7273", "2323"]
FLAT_CODES = ["200", "300", "400", "500", "600", "700"]


class Eltis:
    
    def __init__(self, token):
        self.reset()
        self.stage = 'flat'
        self.flat = choice(token, FLAT_CODES)
        self.fact = choice(token, FACTORY_CODES)
        self.flag = get_flag(token)
        print(f"New session: {self.flat} -> {self.fact}")

    def reset(self):
        self.mode = 'idle'
        self.display = ''
        return f"D:{self.display}"

    def update(self, delta=None, suffix=' '):
        if delta:
            self.display += delta
        pretty_display = self.display.ljust(4, '}')
        pretty_display += suffix
        return f"D:{pretty_display}"
    
    def err(self, code):
        self.reset()
        self.mode = 'error'
        return f"E:{code}"

    def call(self):
        return self.err(6)

    def code(self):
        self.reset()
        self.mode = 'code'
        return "D:C0d3"
    
    def handle(self, btn):
        length = len(self.display)
        if self.mode == 'idle':
            if btn == 'C':
                return self.reset()
            elif btn == 'B':
                if length == 0:
                    return self.code()
                else:
                    return self.call()
            elif length == 5:
                if btn == 'B':
                    return self.call()
                else:
                    return self.err(3)
            else:
                return self.update(btn)
        elif self.mode == 'error':
            if btn == 'C':
                return self.reset()
            else:
                return ''
        elif self.mode == 'code':
            if (self.display + btn) == getattr(self, self.stage):
                if self.stage == 'fact':
                    return f"F:{self.flag}"
                else:
                    print('Going to fact')
                    self.stage = 'fact'
                    return self.reset()
            elif btn == 'C':
                return self.reset()
            elif btn == 'B':
                return self.err(3)
            elif length == 3:
                self.stage = 'flat'
                return self.err(3)
            else:
                return self.update(btn, 'P')

def choice(token, lst):
    return lst[ord(token[-1]) % len(lst)]


def get_flag(token):
    return PREFIX + hmac.new(SECRET2, token.encode(), 'sha256').hexdigest()[:SALT2_SIZE]


def build_app():
    app = web.Application()
    routes = web.RouteTableDef()

    @routes.get('/{token}/')
    async def main(request):
        return web.FileResponse(os.path.join(STATIC_DIR, 'index.html'))

    @routes.get('/{token}/ws')
    async def websocket_handler(request):
        token = request.match_info['token']
        ws = web.WebSocketResponse(heartbeat=5)
        await ws.prepare(request)
        
        eltis = Eltis(token)
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                await ws.send_str(eltis.handle(msg.data))
            elif msg.type == aiohttp.WSMsgType.ERROR:
                return ws

    routes.static('/static', STATIC_DIR)
    
    app.add_routes(routes)
    return app


def start():
    app = build_app()

    if os.environ.get('DEBUG') == 'F':
        web.run_app(app, host='0.0.0.0', port=31337)
    else:
        web.run_app(app, path=os.path.join(sys.argv[1], 'homepage.sock'))


if __name__ == '__main__':
    start()
