#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import aiohttp.web as web
import aiohttp_jinja2 as jinja2
import hmac
import math
import os
import random
import re
import sys
import time

from jinja2 import FileSystemLoader

BASE_DIR = os.path.dirname(__file__)

PREFIX = "ugra_arubaito_toranpu_pasokon_"
SECRET2 = b"villain-pilcrow-yoga-travel-conjugate"
SALT2_SIZE = 12

TARGET = (37.458878, 140.738184)


def dist(lat1, lon1, lat2, lon2):
    R = 6373.0
    lat1, lon1, lat2, lon2 = [math.radians(i) for i in (lat1, lon1, lat2, lon2)]
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def get_flag(token):
    return PREFIX + (hmac.new(SECRET2, token.encode(), 'sha256').hexdigest()[:SALT2_SIZE]
                     .translate(''.maketrans('abcdef', '024689')))


def build_app():
    app = web.Application()
    app["atimes"] = {}
    routes = web.RouteTableDef()

    @routes.get('/{token}/')
    async def root(request):
        token = request.match_info["token"]
        return jinja2.render_template('index.html', request, {})

    async def do_verify(request):
        token = request.match_info["token"]

        ip = request.remote
        atimes = request.app["atimes"]
        if atimes.get(ip, 0) > time.time() - random.randint(3, 10):
            return {"rate_error": True}
        atimes[ip] = time.time()
        if random.random() < 0.01:
            atimes = {i: t for i, t in atimes.items() if t > time.time() - 10}

        form = await request.post()
        data = [form.get(i, "") for i in ["lad", "lam", "las", "lac", "lod", "lom", "los", "loc"]]
        if any(any((c not in "０１２３４５６７８９") for c in i) for i in data):
            return {"presentation_error": True}

        try:
            data = [int(i) for i in data]
        except:
            return {"presentation_error": True}

        lad, lam, las, lac, lod, lom, los, loc = data
        if lad >= 90 or lam >= 60 or las >= 60 or lac >= 100 or lod >= 180 or lom >= 60 or los >= 60 or loc >= 100:
            return {"presentation_error": True}

        la = lad + lam/60 + las/3600 + lac/360000
        lo = lod + lom/60 + los/3600 + loc/360000

        distance = dist(la, lo, *TARGET)

        print("japclock attempt", time.time(), token, *data, distance)

        if distance < 0.0055:
            return {"flag": get_flag(token).split("_")[-1].translate(''.maketrans("0123456789", "零一二三四五六七八九"))}
        else:
            return {"location_error": True}

    @routes.post('/{token}/verify')
    async def verify(request):
        return jinja2.render_template('index.html', request, await do_verify(request))

    app.add_routes(routes)
    jinja2.setup(app, loader=FileSystemLoader(os.path.join(BASE_DIR, 'templates')))
    return app


def start():
    app = build_app()

    if os.environ.get('DEBUG') == 'F':
        web.run_app(app, host='0.0.0.0', port=31337)
    else:
        web.run_app(app, path=os.path.join(sys.argv[1], 'japclock.sock'))


if __name__ == '__main__':
    start()
