# На лечение: Write-up

В таске дан сайт. Его автор предлагает ввести имя пользователя в мессенджере Telegram, обещая рассказать истории и флаги. Звучит заманчиво.

Вводим свой юзернейм, но ничего не выходит — ошибка «Я интроверт и с людьми не общаюсь». Если ввести название канала или чата, то сайт сообщает, что такого пользователя не существует. Вспоминаем, что в телеграме есть ещё и боты. С помощью [@BotFather](https://ucucu.ga/BotFather) регистрируем нового бота и отправляем к нему нашего пациента.

> P.S. Не забудьте удалить бота, если он вам не нужен — его юзернейм может ещё кому-нибудь пригодиться.

Нам сообщают, что пациент ушёл общаться с ботом. Но как же посмотреть историю их переписки? Давайте напишем код, который будет отвечать на сообщения и заодно логгировать их. Можно воспользоваться любым инструментом для обработки обновлений Telegram-ботов, мы попробуем библиотеку [`python-telegram-bot`](https://github.com/python-telegram-bot/python-telegram-bot/). Немного изменим пример `echobot.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import telegram
from telegram.error import NetworkError, Unauthorized
from time import sleep


update_id = None


def main():
    global update_id
    bot = telegram.Bot('TOKEN')

    try:
        update_id = bot.get_updates()[0].update_id
    except IndexError:
        update_id = None

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    while True:
        try:
            echo(bot)
        except NetworkError:
            sleep(1)
        except Unauthorized:
            update_id += 1


def echo(bot):
    global update_id
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1

        if update.message:
            logging.info(update.message.text)


if __name__ == '__main__':
    main()
```

Такой бот будет выводить нам всё, что присылают пользователи. Отправив пациента к боту ещё раз, видим, что он написал `/start Hi! How do you do?`. Вероятно, он ожидает ответа. Модифицируем бота так, чтобы он отвечал отправленным сообщением:

```diff
              logging.info(update.message.text)
+             update.message.reply_text(update.message.text)
```

По логам видим, что бот и пациент вступили в активную полемику. После сотни сообщений в логах видим флаг, а ещё чуть позже пациент успокаивается и перестаёт писать. Наша работа выполнена успешно.

### Альтернативный способ

Был и другой способ решить этот таск: существуют альтернативные Telegram-клиенты, которые позволяют пользоваться ботом так же, как обычным аккаунтом — с интерфейсом и возможностью хранить историю сообщений.

Флаг: **ugra_hi_how_do_you_do_e93f8cdc8eba**.
