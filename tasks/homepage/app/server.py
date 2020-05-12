#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import aiohttp.web as web
import aiohttp_jinja2 as jinja2
import hmac
import os
import re
import sys

from jinja2 import FileSystemLoader

BASE_DIR = os.path.dirname(__file__)
LANGUAGES = ["en", "ru", "hu", "uk"]
ACCEPT_LANGUAGE_RE = r'(?:([a-z]{2,4}|\*)(?:[-_][a-z]{2,4})?)(?:;q=(0\.\d+|0|1))?'

PREFIX = "ugra_what_is_your_erdos_number_"
SECRET2 = b"letter-method-incapable-husband-doubt"
SALT2_SIZE = 12


def get_preferred_language(acceptable):
    regex = re.compile(ACCEPT_LANGUAGE_RE)

    languages = []

    for language in acceptable.split(','):
        match = regex.fullmatch(language.strip().lower())

        if match is None:
            raise web.HTTPBadRequest
        
        language = match.group(1)
        freq = float(match.group(2) or 1)
        
        languages.append((language, freq))
    
    languages.sort(key=lambda l: (-l[1], l[0]))

    for language, freq in languages:
        if language in LANGUAGES:
            return language
    
    return LANGUAGES[0]


def get_flag(token):
    return PREFIX + hmac.new(SECRET2, token.encode(), 'sha256').hexdigest()[:SALT2_SIZE]


def build_app():
    app = web.Application()
    routes = web.RouteTableDef()

    @routes.get('/{token}/')
    async def main(request):
        token = request.match_info['token']

        acceptable = request.headers.get("Accept-Language", "en")
        language = get_preferred_language(acceptable)
                
        return jinja2.render_template(f'{language}.html', request, {"flag": get_flag(token)})

    app.add_routes(routes)
    jinja2.setup(
        app, 
        loader=FileSystemLoader(os.path.join(BASE_DIR, 'templates'))
    )
    return app


def start():
    app = build_app()

    if os.environ.get('DEBUG') == 'F':
        web.run_app(app, host='0.0.0.0', port=31337)
    else:
        web.run_app(app, path=os.path.join(sys.argv[1], 'homepage.sock'))


if __name__ == '__main__':
    start()
