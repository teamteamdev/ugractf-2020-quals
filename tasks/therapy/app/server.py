#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import aiohttp.web as web
import aiohttp_jinja2 as jinja2
import aiosqlite
import asyncio
import datetime
import hmac
import json
import os
import random
import sys
import telethon
import telethon.tl.functions.users as fu

from jinja2 import FileSystemLoader

import writingprompt

BASE_DIR = os.path.dirname(__file__)
STATE_DIR = os.environ.get("STATEDIR", BASE_DIR)
DATABASE = os.path.join(STATE_DIR, "db.sqlite3")

HAPPY_NUMBER = 123

PREFIX = "ugra_hi_how_do_you_do_"
SECRET1 = b"park-snarl-upset-point-harm"
SALT1_SIZE = 16
SECRET2 = b"cower-beam-fail-ghostwriter-benefit"
SALT2_SIZE = 12


def verify_token(token):
    left_token, right_token = token[:SALT1_SIZE], token[SALT1_SIZE:]

    signature = hmac.new(SECRET1, left_token.encode(), 'sha256').hexdigest()[:SALT1_SIZE]

    return signature == right_token


def get_flag(token):
    return PREFIX + hmac.new(SECRET2, token.encode(), 'sha256').hexdigest()[:SALT2_SIZE]


def load_config():
    with open(os.path.join(STATE_DIR, "config.json")) as f:
        return json.loads(f.read())


async def init_database():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS bots (
            token TEXT PRIMARY KEY,
            username TEXT NULL,
            messages INT NOT NULL DEFAULT 0,
            locked BOOL NOT NULL DEFAULT TRUE
        )''')
        await db.commit()


async def get_bot(token):
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM bots WHERE token=:token', {'token': token}) as cur:
            if cur.rowcount == 0:
                return None
            return await cur.fetchone()


async def get_bot_by_username(username):
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM bots WHERE username=:username', {'username': username}) as cur:
            if cur.rowcount == 0:
                return None
            return await cur.fetchone()


async def add_bot(token):
    async with aiosqlite.connect(DATABASE) as db:
        try:
            await db.execute('INSERT INTO bots (token) VALUES (:token)', {
                'token': token
            })

            await db.commit()

            return True
        except:
            return False


async def save_username(token, username):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('UPDATE bots SET username=:username WHERE token=:token', {
            'token': token,
            'username': username
        })
        await db.commit()
        

async def delete_bot(token):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('DELETE FROM bots WHERE token=:token', {'token': token})
        await db.commit()


async def lock_bot(username):
    async with aiosqlite.connect(DATABASE) as db:
        cur = await db.execute('''UPDATE bots SET locked = 1 WHERE username=:username AND locked = 0''', {
            'username': username
        })
        updated = cur.rowcount
        await db.commit()
        return updated == 1


async def unlock_bot(token):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''UPDATE bots SET messages = messages + 1, locked = 0 WHERE token=:token''', {
            'token': token
        })
        await db.commit()


def build_client():
    config = load_config()

    client = telethon.TelegramClient(
        os.path.join(STATE_DIR, "client"), 
        config['api_id'], 
        config['api_hash']
    )
    maker = writingprompt.WritingPromptMaker()


    @client.on(telethon.events.NewMessage)
    async def handle_message(message):
        if not message.is_private:
            return
    
        sender = await message.get_sender()
        username = sender.username.lower()

        if not await lock_bot(username):
            return

        bot = await get_bot_by_username(username)
        if bot['messages'] >= 2 * HAPPY_NUMBER:
            await unlock_bot(bot['token'])
            return

        if bot['messages'] == HAPPY_NUMBER:
            reply = f'{maker.prompt()} {get_flag(bot["token"])}. {maker.prompt()}'
        else:
            reply = ' '.join(
                maker.prompt()
                for _ in range(random.randint(1, 5))
            )
        
        await asyncio.sleep(random.randint(3, 6))
        await unlock_bot(bot['token'])
        await message.reply(reply)

    return client


def build_app(client):
    app = web.Application()
    routes = web.RouteTableDef()


    async def greet(token, peer):
        await asyncio.sleep(3)
        await unlock_bot(token)
        await client.send_message(peer, '/start Hi! How do you do?')


    @routes.get('/{token}/')
    async def main(request):
        token = request.match_info['token']
        error = request.rel_url.query.get('error', '')

        if not verify_token(token):
            raise web.HTTPNotFound
            
        bot = await get_bot(token)

        return jinja2.render_template('index.html', request, {
            'bot': bot,
            'error': error
        })
    

    @routes.post('/{token}/add')
    async def add(request):
        token = request.match_info['token']

        if not verify_token(token):
            raise web.HTTPNotFound

        if not await add_bot(token):
            raise web.HTTPSeeOther(f'/{token}/')

        try:
            form = await request.post()
            username = form.get('username', '').strip().lower()
            if not username:
                raise web.HTTPSeeOther(f'/{token}/?error=Вы+ничего+не+ввели')
                
            if username.startswith('@'):
                username = username[1:]
            
            try:
                info = await client(fu.GetFullUserRequest(username))
            except:
                raise web.HTTPSeeOther(f'/{token}/?error=Такого+пользователя+нет')

            if not info.user.bot:
                raise web.HTTPSeeOther(f'/{token}/?error=Я+интроверт+и+с+людьми+не+общаюсь')
        except:
            await delete_bot(token)
            raise
        
        await save_username(token, username)
        peer = telethon.utils.get_input_peer(info)
        
        asyncio.create_task(greet(token, peer))

        raise web.HTTPSeeOther(f'/{token}/')

    
    @routes.post('/{token}/delete')
    async def delete(request):
        token = request.match_info['token']

        if not verify_token(token):
            raise web.HTTPNotFound
        
        await delete_bot(token)

        raise web.HTTPSeeOther(f'/{token}/')


    app.add_routes(routes)

    jinja2.setup(
        app, 
        loader=FileSystemLoader(os.path.join(BASE_DIR, 'templates'))
    )

    return app


def start():
    client = build_client()
    app = build_app(client)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_database())

    client.start()

    if os.environ.get('DEBUG') == 'F':
        web.run_app(app, host='0.0.0.0', port=31337)
    else:
        web.run_app(app, path=os.path.join(sys.argv[1], 'friends.sock'))


if __name__ == '__main__':
    start()
