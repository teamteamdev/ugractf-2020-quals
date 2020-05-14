#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=unused-variable

import aiohttp.web as web
import aiohttp_jinja2 as jinja2
import aiohttp_session as sessions
import aiohttp_session.cookie_storage as storage
import aiosqlite
import asyncio
import base64
import functools
import hashlib
import hmac
import io
import os
import qrcode
import secrets
import struct
import sys
import time

from jinja2 import FileSystemLoader

BASE_DIR = os.path.dirname(__file__)
DATABASE = os.path.join(os.environ.get("STATEDIR", BASE_DIR), "db.sqlite3")

PREFIX = "ugra_oh_no_totp_secret_leaked_"
SECRET2 = b"reflect-implication-article-action-dominant"
SALT2_SIZE = 12

ADMIN_USER_ID = 1


def get_flag(token):
    return PREFIX + hmac.new(SECRET2, token.encode(), 'sha256').hexdigest()[:SALT2_SIZE]


async def init_database():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            created DATETIME DEFAULT current_timestamp,
            UNIQUE (username) ON CONFLICT ABORT
        )''')

        await db.execute('''INSERT OR IGNORE INTO users (id, username, created) VALUES
            (1, "admin", "2020-04-17 21:27:15"),
            (2, "gena", "2020-04-17 22:05:49"),
            (3, "basil", "2020-04-18 14:20:27")''')

        await db.execute('''CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY,
            source_id INTEGER NOT NULL,
            target_id INTEGER NOT NULL,
            created DATETIME DEFAULT current_timestamp
        )''')

        await db.commit()


def build_app():
    app = web.Application()
    routes = web.RouteTableDef()


    def check_session(state):
        def inner(func):
            @functools.wraps(func)
            async def wrapper(request):
                token = request.match_info['token']
                session = await sessions.get_session(request)

                if session.setdefault('state', 'login') == state:
                    return await func(request)
                
                if session.get('state') == 'user':
                    raise web.HTTPSeeOther(f'/{token}/users/{session["user_id"]}')
                elif session.get('state') == 'pass':
                    raise web.HTTPSeeOther(f'/{token}/password')
                else:
                    raise web.HTTPSeeOther(f'/{token}/login')
            
            return wrapper
        return inner


    async def get_users():
        async with aiosqlite.connect(DATABASE) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM users') as cur:
                return await cur.fetchall()
    

    async def get_user(user_id):
        async with aiosqlite.connect(DATABASE) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM users WHERE id=:id', {'id': user_id}) as cur:
                if cur.rowcount == 0:
                    raise web.HTTPNotFound
                return await cur.fetchone()


    async def get_user_by_username(username):
        async with aiosqlite.connect(DATABASE) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM users WHERE username=:username', {'username': username}) as cur:
                if cur.rowcount == 0:
                    return None
                return await cur.fetchone()


    async def create_user(username):
        async with aiosqlite.connect(DATABASE) as db:
            async with db.execute('INSERT INTO users (username) VALUES (:username)', {'username': username}) as cur:
                user_id = cur.lastrowid
            
            await db.commit()

            return user_id
    

    async def is_friend_of(source_id, target_id):
        async with aiosqlite.connect(DATABASE) as db:
            async with db.execute(
                'SELECT count(*) % 2 FROM friends WHERE source_id=:source_id AND target_id=:target_id', {
                    'source_id': source_id, 
                    'target_id': target_id
                }) as cur:
                status, = await cur.fetchone()
                return bool(status)


    def get_hotp_token(secret, intervals_no):
        key = base64.b32decode(secret, True)
        msg = struct.pack(">Q", intervals_no)
        h = hmac.new(key, msg, hashlib.sha1).digest()
        o = h[19] & 15
        h = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1000000
        return h


    def get_totp_token(secret):
        return get_hotp_token(secret, intervals_no=int(time.time())//30)


    def get_otp_secret(user_id):
        return base64.b32encode(f'user_id={f"{user_id}".rjust(12, "0")}'.encode()).decode()


    @routes.get('/{token}/')
    @check_session('main')
    async def main(request):
        # it should never come here
        pass


    @routes.get('/{token}/login')
    @check_session('login')
    async def login_page(request):
        error = request.rel_url.query.get('error', '')
        return jinja2.render_template(f'login.html', request, {'error': error})
    

    @routes.post('/{token}/login')
    @check_session('login')
    async def check_login(request):
        token = request.match_info['token']

        form = await request.post()
        username = form.get('username', '').strip()
        if not username:
            raise web.HTTPSeeOther(f'/{token}/login?error=Как+же+Вы+без+логина%3F%3F%3F')
        
        user = await get_user_by_username(username)
        if user is None:
            raise web.HTTPSeeOther(f'/{token}/login?error=Откуда+хоть+вы+этот+логин+взяли%3F%3F%3F')

        session = await sessions.get_session(request)
        session['state'] = 'pass'
        session['user_id'] = user['id']
        raise web.HTTPSeeOther(f'/{token}/password')


    @routes.get('/{token}/register')
    @check_session('login')
    async def register_page(request):
        error = request.rel_url.query.get('error', '')
        return jinja2.render_template(f'register.html', request, {'error': error})
    

    @routes.post('/{token}/register')
    @check_session('login')
    async def check_register(request):
        token = request.match_info['token']

        form = await request.post()
        username = form.get('username', '').strip()
        if not username:
            raise web.HTTPSeeOther(f'/{token}/register?error=Как+же+Вы+без+логина%3F%3F%3F')

        user = await get_user_by_username(username)
        if user is not None:
            raise web.HTTPSeeOther(f'/{token}/register?error=Такой+логин+уже+есть,+входите+же!!!')

        try:
            user_id = await create_user(username)
        except aiosqlite.IntegrityError:
            raise web.HTTPSeeOther(f'/{token}/register?error=Ну+что+же+вы+по+два+раза+кнопки-то+нажимаете%3F%3F%3F')

        session = await sessions.get_session(request)
        session['state'] = 'user'
        session['user_id'] = user_id
        raise web.HTTPSeeOther(f'/{token}/users/{user_id}')
    

    @routes.get('/{token}/password')
    @check_session('pass')
    async def password_page(request):
        error = request.rel_url.query.get('error', '')
        return jinja2.render_template(f'password.html', request, {'error': error})


    @routes.post('/{token}/password')
    @check_session('pass')
    async def check_password(request):
        token = request.match_info['token']
        session = await sessions.get_session(request)
        user_id = session['user_id']

        secret = get_otp_secret(user_id)
        real_password = get_totp_token(secret)

        form = await request.post()
        password = form.get('password', '').strip()

        if password != str(real_password):
            raise web.HTTPSeeOther(f'/{token}/password?error=И+что+это+за+пароль+такой%3F%3F%3F')

        session['state'] = 'user'
        raise web.HTTPSeeOther(f'/{token}/users/{user_id}')


    @routes.post('/{token}/users/{target_id}')
    @check_session('user')
    async def add_friend(request):
        token = request.match_info['token']
        session = await sessions.get_session(request)

        user_id = session['user_id']
        try:
            target_id = int(request.match_info['target_id'])
        except ValueError:
            raise web.HTTPBadRequest

        async with aiosqlite.connect(DATABASE) as db:
            await get_user(target_id)

            await db.execute('INSERT INTO friends (source_id, target_id) VALUES (:source_id, :target_id)', {
                "source_id": user_id, 
                "target_id": target_id
            })

            await db.commit()

            return web.HTTPSeeOther(f'/{token}/users/{target_id}')


    @routes.get('/{token}/users/{target_id}')
    @check_session('user')
    async def profile(request):
        token = request.match_info['token']
        session = await sessions.get_session(request)

        user_id = session['user_id']
        try:
            target_id = int(request.match_info['target_id'])
        except ValueError:
            raise web.HTTPBadRequest

        context = {
            'user_id': user_id,
            'user': await get_user(target_id),
            'personal': user_id == target_id,
            'token': token
        }
        
        if user_id == target_id:
            context['note'] = get_flag(token) if user_id == ADMIN_USER_ID else ''
        else:
            context['is_friend'] = await is_friend_of(user_id, target_id)
            context['is_friend_of'] = await is_friend_of(target_id, user_id)

        return jinja2.render_template('user.html', request, context)
    

    @routes.get('/{token}/qr')
    @check_session('user')
    async def qr(request):
        session = await sessions.get_session(request)
        user_id = session['user_id']
        
        secret = get_otp_secret(user_id)
        user = await get_user(user_id)

        qr = qrcode.make(f'otpauth://totp/friends:{user["username"]}?secret={secret}&issuer=friends')
        data = io.BytesIO()
        qr.save(data, format='png')

        return web.Response(body=data.getvalue(), headers={'Content-Type': 'image/png'})
    

    @routes.get('/{token}/users')
    @check_session('user')
    async def users(request):
        token = request.match_info['token']
        session = await sessions.get_session(request)
        user_id = session['user_id']

        return jinja2.render_template('users.html', request, {
            'users': await get_users(),
            'token': token,
            'user_id': user_id
        })
    

    @routes.get('/{token}/logout')
    @check_session('user')
    async def logout(request):
        token = request.match_info['token']

        session = await sessions.get_session(request)
        session['state'] = 'login'
        session.pop('user_id')

        raise web.HTTPSeeOther(f'/{token}/login')



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

    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_database())

    if os.environ.get('DEBUG') == 'F':
        web.run_app(app, host='0.0.0.0', port=31337)
    else:
        web.run_app(app, path=os.path.join(sys.argv[1], 'friends.sock'))


if __name__ == '__main__':
    start()
