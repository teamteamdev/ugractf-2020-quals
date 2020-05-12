#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import aiohttp.web as web
import aiohttp_jinja2 as jinja2
import aiohttp_session as sessions
import aiohttp_session.cookie_storage as storage
import base64
import functools
import hmac
import io
import os
import qrcode
import re
import secrets
import sys

from jinja2 import FileSystemLoader

BASE_DIR = os.path.dirname(__file__)

PREFIX = "ugra_oh_no_totp_secret_leaked_"
SECRET2 = b"reflect-implication-article-action-dominant"
SALT2_SIZE = 12

ADMIN_USER_ID = 1


def get_flag(token):
    return PREFIX + hmac.new(SECRET2, token.encode(), 'sha256').hexdigest()[:SALT2_SIZE]


def build_app():
    app = web.Application()
    routes = web.RouteTableDef()

    def check_session(state):
        def inner(func):
            @functools.wraps(func)
            async def wrapper(request):
                token = request.match_info['token']
                session = await sessions.get_session(request)

                if session.get('state') == state:
                    return await func(request)
                
                if session.get('state') == 'user':
                    raise web.HTTPSeeOther(f'/{token}/my')
                elif session.get('state') == 'pass':
                    raise web.HTTPSeeOther(f'/{token}/password')
                else:
                    raise web.HTTPSeeOther(f'/{token}/login')
            
            return wrapper
        return inner

    @routes.get('/{token}/')
    @check_session('main')
    async def main(request):
        # it should never come here
        pass

    @routes.get('/{token}/login')
    async def login_page(request):
        return jinja2.render_template(f'login.html', request, {})
    
    @routes.post('/{token}/login')
    async def check_login(request):
        token = request.match_info['token']
        session = await sessions.get_session(request)
        session['state'] = 'pass'
        session['user_id'] = 1
        raise web.HTTPSeeOther(f'/{token}/password')
    
    @routes.get('/{token}/password')
    @check_session('pass')
    async def password_page(request):
        return jinja2.render_template(f'password.html', request, {})

    @routes.post('/{token}/password')
    @check_session('pass')
    async def check_password(request):
        token = request.match_info['token']
        session = await sessions.get_session(request)
        session['state'] = 'user'
        raise web.HTTPSeeOther(f'/{token}/my')

    @routes.get('/{token}/my')
    @check_session('user')
    async def my(request):
        token = request.match_info['token']
        session = await sessions.get_session(request)

        user_id = session['user_id']
        note = get_flag(token) if session['user_id'] == ADMIN_USER_ID else ''

        return jinja2.render_template('my.html', request, {
            "note": note
        })
    
    @routes.get('/{token}/qr')
    @check_session('user')
    async def qr(request):
        session = await sessions.get_session(request)
        secret = base64.b32encode(f"user_id={str(session['user_id']).rjust(12, '0')}".encode()).decode()

        qr = qrcode.make(
            f'otpauth://totp/ugrauth:user?secret={secret}&issuer=ugrauth'
        )

        data = io.BytesIO()
        qr.save(data, format='png')

        return web.Response(body=data.getvalue(), headers={"Content-Type": "image/png"})
    

    @routes.get('/{token}/users')
    @check_session('user')
    async def users(request):
        return jinja2.render_template('users.html', request, {"users": []})

    app.add_routes(routes)

    jinja2.setup(
        app, 
        loader=FileSystemLoader(os.path.join(BASE_DIR, 'templates'))
    )

    sessions.setup(
        app,
        storage.EncryptedCookieStorage(secrets.token_bytes(32))
    )

    return app


def start():
    app = build_app()

    if os.environ.get('DEBUG') == 'F':
        web.run_app(app, host='0.0.0.0', port=31337)
    else:
        web.run_app(app, path=os.path.join(sys.argv[1], 'auth.sock'))


if __name__ == '__main__':
    start()
