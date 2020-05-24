#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import flask
import hmac
import os
import sqlite3
import telegram

from config import TOKEN

PREFIX = "ugra_thanks_for_good_photo_"
SECRET1 = b"seed-chapter-doctor-dialogue-bus"
SALT1_SIZE = 10
SECRET2 = b"dignity-update-coat-compensation-brand"
SALT2_SIZE = 12

app = flask.Flask(__name__)
bot = telegram.Bot(TOKEN)

def verify_token(token):
    left_token, right_token = token[:SALT1_SIZE], token[SALT1_SIZE:]

    signature = hmac.new(SECRET1, left_token.encode(), 'sha256').hexdigest()[:SALT1_SIZE]

    return signature == right_token


def get_flag(token):
    return PREFIX + hmac.new(SECRET2, token.encode(), 'sha256').hexdigest()[:SALT2_SIZE]


def query_select(*args):
    with sqlite3.connect('db.sqlite3') as db:
        db.row_factory = sqlite3.Row
        cur = db.execute(*args)
        return cur.fetchall()


def query_insert(*args):
    with sqlite3.connect('db.sqlite3') as db:
        db.execute(*args)
        db.commit()


@app.route('/')
def messages():
    rows = query_select('SELECT * FROM messages ORDER BY created DESC')

    closed = query_select('SELECT * FROM users')
    closed = {
        row['user_id']: bool(row['closed'])
        for row in closed
    }

    users = set(map(lambda x: x['user_id'], rows))

    userrows = {
        user: {
            'messages': list(filter(lambda x: x['user_id'] == user, rows))
        }
        for user in users
    }

    for user, obj in userrows.items():
        obj['last'] = max(*list(map(lambda x: x['created'], obj['messages'])))
        obj['closed'] = closed.get(user, False)
        obj['message'] = obj['messages'][0]
    
    conversations = sorted(userrows.items(), key=lambda x: x[1]['last'], reverse=True)

    return flask.render_template('list.html', conversations=conversations, closed=flask.request.args.get('closed') == 'true')
    

@app.route('/<int:user_id>/')
def get_conversation(user_id):
    rows = query_select('SELECT * FROM messages WHERE user_id=:user_id ORDER BY created DESC', {'user_id': user_id})
    closed = query_select('SELECT * FROM users WHERE user_id=:user_id', {'user_id': user_id})
    try:
        closed = closed[0]['closed']
    except:
        closed = False
    
    return flask.render_template('conversation.html', user_id=user_id, messages=rows, closed=closed)


def close(user_id):
    query_insert('UPDATE users SET closed=1 WHERE user_id=:user_id', {'user_id': user_id})


@app.route('/<int:user_id>/token', methods=['POST'])
def send_flag(user_id):
    token = flask.request.form.get('token', '').lower().strip()
    if not verify_token(token):
        return flask.redirect(f'/{user_id}/?token={token}&reason_token=Bad+token')
    
    flag = get_flag(token)
    message = f"Отлично! Вот ваш флаг: `{flag}`."
    bot.send_message(
        chat_id=user_id,
        text=message,
        parse_mode="Markdown"
    )

    query_insert('''INSERT INTO messages (user_id, out, text, token) VALUES (:user_id, 1, :text, :token)''', {
        'user_id': user_id,
        'text': message,
        'token': token
    })
    close(user_id)

    return flask.redirect(f'/{user_id}/')


@app.route('/<int:user_id>/write', methods=["POST"])
def send_message(user_id):
    message = flask.request.form.get('message', '')

    if not message:
        return flask.redirect(f'/{user_id}/?reason_message=No+message')

    bot.send_message(
        chat_id=user_id,
        text=message,
        parse_mode="Markdown"
    )

    query_insert('''INSERT INTO messages (user_id, out, text, token) VALUES (:user_id, 1, :text, :token)''', {
        'user_id': user_id,
        'text': message,
        'token': ''
    })
    close(user_id)

    return flask.redirect(f'/{user_id}/')


@app.route('/<int:user_id>/close')
def close_conversation(user_id):
    close(user_id)

    return flask.redirect(f'/{user_id}/')



if __name__ == "__main__":
    app.run(port=7752)
