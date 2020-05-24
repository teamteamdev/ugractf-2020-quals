#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import telegram.ext
import sqlite3

from config import TOKEN

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def query(*args):
    with sqlite3.connect('db.sqlite3') as db:
        db.execute(*args)
        db.commit()


def init():
    query('''CREATE TABLE IF NOT EXISTS messages (
 id INTEGER PRIMARY KEY,
 user_id INTEGER NOT NULL,
 out INTEGER NOT NULL,
 created DATETIME NOT NULL DEFAULT current_timestamp,
 text TEXT NOT NULL,
 token TEXT NOT NULL DEFAULT ''
)''')
    query('''CREATE TABLE IF NOT EXISTS users (
 user_id INTEGER PRIMARY KEY,
 closed INTEGER NOT NULL
)''')


def he(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def start(update, context):
    update.message.reply_text('Привет! Отправь ссылку на фотографию, и её проверят.')


def process(update, context):
    if not update.message.text:
        update.message.reply_text('Я не понимаю твоё сообщение, я читаю лишь ссылки.')
        return
    
    urls = []
    if update.message.entities:
        for entity in update.message.entities:
            if entity.type == "url":
                urls.append((entity.offset, entity.length))
    
    urls.sort(key=lambda x: x[0])

    origin = update.message.text
    text = ""
    i = 0
    for offset, length in urls:
        text += origin[i:offset]
        text += '<a href="'
        text += origin[offset:offset+length].replace('>', '').replace('"', '')
        text += '">'
        text += he(origin[offset:offset+length])
        text += '</a>'
        i = offset + length
    text += he(origin[i:])

    query('''INSERT OR REPLACE INTO users (user_id, closed) VALUES (:uid, 0)''', {
        'uid': update.message.from_user.id
    })
    query('''INSERT INTO messages (user_id, out, text) VALUES (:uid, 0, :text)''', {
        'uid': update.message.from_user.id,
        'text': text
    })

    update.message.reply_text('Ожидайте ответа...')


def error(update, context):
    logging.error('Update "%s" caused eror "%s"', update, context.error)


def main():
    init()

    updater = telegram.ext.Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(telegram.ext.CommandHandler("start", start))
    dp.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.text, process))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
