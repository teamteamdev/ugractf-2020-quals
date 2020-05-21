#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import aiohttp.web as web
import aiohttp_jinja2 as jinja2
import datetime
import functools
import hmac
import motor.motor_asyncio as motor
import os
import sys
import urllib.parse

from jinja2 import FileSystemLoader

BASE_DIR = os.path.dirname(__file__)
STATE_DIR = sys.argv[1] if len(sys.argv) >= 2 else BASE_DIR
ADMIN_CREDS = (
    os.environ['MONGO_USER'],
    os.environ['MONGO_PASS']
)
MONGO_PATH = f'mongodb://{{}}:{{}}@{urllib.parse.quote_plus(os.path.join(STATE_DIR, "mongo.sock"))}/db?authSource=admin'

PREFIX = 'ugra_validate_user_input_'
SECRET1 = b'coach-pot-groan-funeral-pin'
SALT1_SIZE = 16
SECRET2 = b'action-career-argument-extension-distributor'
SALT2_SIZE = 12


def verify_token(token):
    left_token, right_token = token[:SALT1_SIZE], token[SALT1_SIZE:]

    signature = hmac.new(SECRET1, left_token.encode(), 'sha256').hexdigest()[:SALT1_SIZE]

    return signature == right_token


def get_flag(token):
    return PREFIX + hmac.new(SECRET2, token.encode(), 'sha256').hexdigest()[:SALT2_SIZE]


def get_posts(token):
    return [
        {'author': 'secretleetuser1337', 'text': get_flag(token), 'date': datetime.datetime(2020, 3, 25, 3, 13, 37, 156000)},
        {'author': 'nagibator1976', 'text': 'а как тут ставить лайки?', 'date': datetime.datetime(2020, 3, 30, 17, 56, 20, 346000)},
        {'author': 'mike', 'text': 'Привет мои дорогие читатели!', 'date': datetime.datetime(2020, 4, 1, 4, 20, 0, 926000)},
        {'author': 'semurg', 'text': 'В этом выпуске моего блога вы узнаете, как экономить на клее с помощью асбеста', 'date': datetime.datetime(2020, 4, 3, 15, 27, 32, 517000)},
        {'author': 'jorik', 'text': 'Чтобы повысить зарплату в два раза, скажите прорабу ЭТИ ДВА СЛОВА...', 'date': datetime.datetime(2020, 4, 9, 17, 2, 25, 86000)},
        {'author': 'mikhalych', 'text': '10 лайфхаков для эффективной кладки кирпичей!', 'date': datetime.datetime(2020, 4, 12, 14, 58, 12, 392000)},
        {'author': 'ivan', 'text': 'Я сегодня поработал на стройке новой школы, не отдавайте туда своих детей никогда!', 'date': datetime.datetime(2020, 4, 16, 5, 0, 19, 193000)}
    ]


def build_app():
    app = web.Application()
    routes = web.RouteTableDef()

    def authorize_team(func):
        @functools.wraps(func)
        async def wrapper(request):
            client = motor.AsyncIOMotorClient(MONGO_PATH.format(*ADMIN_CREDS))
            token = request.match_info['token']

            if not verify_token(token):
                raise web.HTTPNotFound

            admin = client.admin
            db = client.db

            if token not in await db.list_collection_names():
                await admin.command(
                    'createRole',
                    token,
                    privileges=[{
                        'resource': {
                            'db': 'db',
                            'collection': token
                        },
                        'actions': ['find', 'insert']
                    }],
                    roles=[]
                )

                await admin.command(
                    'createUser',
                    token,
                    pwd=token,
                    roles=[token]
                )

                await db[token].insert_many(get_posts(token))

            return await func(request)

        return wrapper

    async def get_articles_query(db, token, query=None):
        posts = await db[token].find(
            query,
            limit=5,
            sort=[('date', -1)]
        ).to_list(None)

        for post in posts:
            post['_id'] = str(post.get('_id', None))
            post['date'] = str(post.get('date', None))

        return web.json_response(posts)
    
    @routes.get('/{token}/articles')
    @authorize_team
    async def get_articles(request):
        token = request.match_info['token']
        db = motor.AsyncIOMotorClient(MONGO_PATH.format(token, token)).db

        return await get_articles_query(db, token)
    
    @routes.post('/{token}/articles')
    @authorize_team
    async def get_articles_by(request):
        token = request.match_info['token']
        db = motor.AsyncIOMotorClient(MONGO_PATH.format(token, token)).db

        try:
            query = await request.json()
        except:
            raise web.HTTPBadRequest()

        return await get_articles_query(db, token, query)
    
    @routes.post('/{token}/')
    @authorize_team
    async def create_post(request):
        token = request.match_info['token']
        db = motor.AsyncIOMotorClient(MONGO_PATH.format(token, token)).db

        try:
            query = await request.post()
        except:
            raise web.HTTPBadRequest()

        if 'author' not in query or 'text' not in query:
            raise web.HTTPBadRequest()

        await db[token].insert_one({
            'author': query['author'],
            'text': query['text'],
            'date': datetime.datetime.now()
        })

        return web.HTTPSeeOther(f'/{token}/')

    @routes.get('/{token}/')
    @authorize_team
    async def main(request):
        return jinja2.render_template('main.html', request, {})

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
        web.run_app(app, path=os.path.join(STATE_DIR, 'mybrick.sock'))


if __name__ == '__main__':
    start()
