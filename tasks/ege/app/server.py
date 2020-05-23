#!/usr/bin/env python3
# -*- coding: utf-8 _*_

import asyncio
import os
import sys
from random import choice
import hmac

GRAM = {
    'm': 'обидва',
    'f': 'обидві',
    'n': 'обоє',
    'anim': 'хто',
    'inanim': 'що',
    'unanim': 'що'
    }

BASE_DIR = os.path.dirname(__file__)
MAX_SCORE = 1337
MAX_ERRORS = 30

PREFIX = "ugra_durnytsya_dribnitsya_"
SECRET1 = b"daily-schedule-note-sum"
SALT1_SIZE = 32
SECRET2 = b"i-tried-clojure-before-and-it-went-bad"
SALT2_SIZE = 12

GREETING = "Вас вітає електросистема оцінки знань в рамках підготовки до ЕГЭ!\n\n" \
    "Введіть код учасника: "

FINISH = "\nРозминка успішно пройдена.\n\n" \
    "ЗАВДАННЯ 2.\n" \
    "Напишіть есе на тему «{}» (1000-1020 слів). " \
    "Відправляти результат сюди не вимагається.\n\n" \
    "Успіхів!\n"

def read_dict(file):
    file = open(file, 'r').read().split('\n')
    i = iter(file)
    return list(zip(i, i))


def parse_word(w):
    word, form = [x.split(':') for x in w]
    return {
        'singular': word[0].split()[0],
        'plural': form[0].strip().split()[0],
        'type': form[1],
        'gender': word[2]
    }


def test_word(word):
    rules = [word.get('gender') != 'p',
             word.get('type'),
             word.get('plural'),
             word.get('singular') != word.get('plural')
             ]
    return all(rules)


def load_dict(file):
    print("Loading dictionary...")
    return list(map(parse_word, read_dict(file)))


def challenge(dictionary):
    word = choice(dictionary)
    while not test_word(word):
        word = choice(dictionary)

    question = f"\n{word['plural'].title()} — вони {GRAM[word['type']]}?\n" \
        "Ваш варіант (обидва, обидві, обоє): "
    answer = GRAM[word['gender']]
    return (question, answer)


def humiliate(score):
    return f"\nЗАВДАННЯ 1. Частина {score + 1}/{MAX_SCORE}."


def generate_flag(token):
    return PREFIX + hmac.new(SECRET2, token.encode(), "sha256").hexdigest()[:SALT2_SIZE]


async def game(reader, writer):
    async def send(msg):
        writer.write(msg.encode('utf8'))
        await writer.drain()

    async def recv():
        data = await reader.readline()
        if data:
            return data.decode().strip().lower()
        else:
            return ""

    score = 0
    errors = 0

    await send(GREETING)
    token = await recv()    
    while len(token) < 3:
        await send("Ні, ще раз: ")
        token = await recv()
    
    while score < MAX_SCORE and errors < MAX_ERRORS:
        await send(humiliate(score))
        q, a = challenge(words)
        await send(q)
        user_a = await recv()
        if user_a == a:
            await send("Так.\n")
            score += 1
        else:
            await send("Ні!\n")
            errors += 1

    if score == MAX_SCORE:
        await send(FINISH.format(generate_flag(token)))
    elif errors == MAX_ERRORS:
        await send("\nВи якщо ВГАДАТИ хочете, ви ЙДІТЬ ЗВІДСИ.\n")
    else:
        await send("Ну тоді до побачення!\n")

    writer.close()


def start():
    loop = asyncio.get_event_loop()
    if os.environ.get('DEBUG') == 'F':
        coro = asyncio.start_server(game, '127.0.0.1', 31337, loop=loop)
    else:
        coro = asyncio.start_unix_server(game, os.path.join(sys.argv[1], "ege.sock"), loop=loop)
    print('Starting server...')
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == "__main__":
    words = load_dict(os.path.join(BASE_DIR, "dict.txt"))
    start()
