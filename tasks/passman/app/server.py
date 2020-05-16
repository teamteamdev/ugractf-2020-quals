#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=unused-variable

import aiohttp.web as web
import aiohttp_jinja2 as jinja2
import aiosqlite
import asyncio
import base64
import functools
import hashlib
import hmac
import json
import os
import re
import sys
import time

from jinja2 import FileSystemLoader

BASE_DIR = os.path.dirname(__file__)
DATABASE = os.path.join(os.environ.get("STATEDIR", BASE_DIR), "db.sqlite3")

PREFIX = "ugra_lets_forget_xor_forever_"
SECRET2 = b"lamb-access-concede-prey-stage"
SALT2_SIZE = 12

ADMIN_USER_ID = 1
COOKIE_SECRET = b"\x92]\x1c\xfa\x1akG\x15;]\xddJ\xaa\x07,\xa7e\xb6\xe8\xddR!\xdeY\xdd\x03\x82\xe2$\xd3\r#Gl\xff\x03\xce0d\xd8\x0b\x89\x06M\xb5\x8f,\x02\x00\x9d\x06\xc8\xa0\x8akN\x85\xbe7\xce8\xc6*\xb2\xf6\x99\xe8\xf9\xcd\xc2\x83\xff=\x05u\xc7[\xaf\xa3\xb9\xb8\x97\xa5\x97]\x13\x1as\xce\xb5\x0e\xca\xc9w\xf9\x851p\xa9v\x98Gg\x10s\xcb$,\x0f\xc0\xe4B\x11lJ\x86\xb5 \xca\xd7\x8dM\xff#\x9b%\xb5q"


def get_flag(token):
    return PREFIX + hmac.new(SECRET2, token.encode(), 'sha256').hexdigest()[:SALT2_SIZE]


async def init_database():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            created DATETIME DEFAULT current_timestamp,
            UNIQUE (username) ON CONFLICT ABORT
        )''')

        await db.execute('''INSERT OR IGNORE INTO users (id, username, password, created) VALUES
            (1, 'admin', '*', '2020-05-12 03:13:37')''')

        await db.execute('''CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            password TEXT NOT NULL,
            created DATETIME DEFAULT current_timestamp
        )''')

        await db.commit()


async def create_user(username, password):
    async with aiosqlite.connect(DATABASE) as db:
        try:
            await db.execute('INSERT INTO users (username, password) VALUES (:username, :password)', {
                'username': username,
                'password': password
            })
            await db.commit()
            return True
        except:
            return False


async def get_user_by_username(username):
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM users WHERE username=:username', {'username': username}) as cur:
            if cur.rowcount == 0:
                return None
            return await cur.fetchone()


async def get_passwords(user_id):
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM passwords WHERE user_id=:id', {'id': user_id}) as cur:
            return await cur.fetchall()


async def create_password(user_id, description, password):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('INSERT INTO passwords (user_id, description, password) VALUES (:user_id, :description, :password)', {
            'user_id': user_id,
            'description': description,
            'password': password
        })
        await db.commit()


async def delete_password(user_id, password_id):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('DELETE FROM passwords WHERE user_id=:user_id AND id=:id', {'user_id': user_id, 'id': password_id})
        await db.commit()


async def get_user_by_cookie(session):
    if len(session) > len(COOKIE_SECRET):
        return False
    
    try:
        encrypted_cookie = base64.b64decode(session)
        decrypted_cookie = bytearray([
            i ^ j for i, j in zip(COOKIE_SECRET, encrypted_cookie)
        ])

        payload = json.loads(decrypted_cookie)

        assert type(payload.get('created')) == int
        assert type(payload.get('username')) == str
        assert len(payload) == 2
    except Exception as e:
        return None
    
    return await get_user_by_username(payload['username'])


def build_app():
    app = web.Application()
    routes = web.RouteTableDef()


    def check_user(*, should_login):
        def inner(func):
            @functools.wraps(func)
            async def wrapper(request):
                token = request.match_info['token']

                cookie = request.cookies.get('session', '')

                if not should_login:
                    if cookie == '':
                        return await func(request)
                    else:
                        raise web.HTTPSeeOther(f'/{token}/passwords')

                if cookie is None and not should_login:
                    return await func(request)
                
                user = await get_user_by_cookie(cookie)

                if user is None:
                    raise web.HTTPSeeOther(
                        f'/{token}/',
                        headers={
                            'Set-Cookie': 'session=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT',
                            'X-Error': 'Invalid cookie'
                        }
                    )
                
                request.user = user
                return await func(request)
            
            return wrapper
        return inner


    @routes.get('/{token}/')
    @check_user(should_login=False)
    async def main(request):
        error = request.rel_url.query.get('error', '')
        return jinja2.render_template(f'login.html', request, {'error': error})


    @routes.post('/{token}/login')
    @check_user(should_login=False)
    async def login(request):
        token = request.match_info['token']

        form = await request.post()
        username = form.get('username', '').strip()
        password = form.get('password', '').strip()
        if not username or not password:
            raise web.HTTPSeeOther(f'/{token}/?error=Заполните+все+поля')
        
        if not re.fullmatch('[a-zA-Z0-9-]{,32}', username):
            raise web.HTTPSeeOther(f'/{token}/?error=Заполните+поле+username+правильно')
        
        password = hashlib.sha512(password.encode()).hexdigest()
        
        user = await get_user_by_username(username)
        if user is None:
            if not await create_user(username, password):
                raise web.HTTPSeeOther(f'/{token}/?error=Повторите+запрос')
        elif user['password'] != password:
            raise web.HTTPSeeOther(f'/{token}/?error=Пароль+неверный')
            
        payload = json.dumps({
            'created': int(time.time()),
            'username': username
        }).encode()

        encrypted = bytearray([
            i ^ j for i, j in zip(COOKIE_SECRET, payload)
        ])
        
        session = base64.b64encode(encrypted).decode()
        
        raise web.HTTPSeeOther(f'/{token}/passwords', headers={
            'Set-Cookie': f'session={session}; path=/'
        })


    @routes.get('/{token}/passwords')
    @check_user(should_login=True)
    async def passwords(request):
        token = request.match_info['token']
        user_id = request.user['id']

        error = request.rel_url.query.get('error', '')
        flag = get_flag(token) if user_id == ADMIN_USER_ID else None
        passwords = await get_passwords(user_id)
        
        return jinja2.render_template(f'passwords.html', request, {
            'error': error,
            'flag': flag,
            'passwords': passwords,
            'user': request.user
        })
    

    @routes.post('/{token}/passwords')
    @check_user(should_login=True)
    async def handle_create_password(request):
        token = request.match_info['token']

        form = await request.post()
        description = form.get('description', '').strip()
        password = form.get('password', '').strip()
        if not description or not password:
            raise web.HTTPSeeOther(f'/{token}/passwords?error=Заполните+все+поля')
        
        await create_password(request.user['id'], description, password)

        raise web.HTTPSeeOther(f'/{token}/passwords')
    

    @routes.post('/{token}/passwords/{password_id}')
    @check_user(should_login=True)
    async def handle_delete_password(request):
        token = request.match_info['token']
        password_id = request.match_info['password_id']

        await delete_password(request.user['id'], password_id)

        raise web.HTTPSeeOther(f'/{token}/passwords')
    

    @routes.get('/{token}/logout')
    @check_user(should_login=True)
    async def logout(request):
        token = request.match_info['token']

        raise web.HTTPSeeOther(
            f'/{token}/',
            headers={
                'Set-Cookie': 'session=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT'
            }
        )


    app.add_routes(routes)

    jinja2.setup(
        app, 
        loader=FileSystemLoader(os.path.join(BASE_DIR, 'templates'))
    )

    return app


def start():
    app = build_app()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_database())

    if os.environ.get('DEBUG') == 'F':
        web.run_app(app, host='0.0.0.0', port=31337)
    else:
        web.run_app(app, path=os.path.join(sys.argv[1], 'passman.sock'))


if __name__ == '__main__':
    start()
