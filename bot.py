import telebot
import config
import item_base
import random
import requests
import pars
import token_base
import numpy as np
import pandas as pd
import os

bot = telebot.TeleBot(config.TOKEN)

URL = 'https://api.telegram.org/bot'


def get_updates(offset=0):
    result = \
        requests.get(f'{URL}{config.TOKEN}/getUpdates?offset={offset}').json()
    return result['result']


def send_doc_file(chat_id, doc):
    files = {'document': open(doc, 'rb')}
    requests.post(
        f'{URL}{config.TOKEN}/sendDocument?chat_id={chat_id}', files=files)


def check_token(message, token=None):
    if (token is None):
        token = token_base.cur_token
    if (token in token_base.token_base):
        token_base.cur_token = token
        return True
    bot.send_message(message.chat.id, "Ваш токен не найден в базе")
    return False


def check_base(message):
    if (len(item_base.items) == 0):
        bot.send_message(message.chat.id, "Нет предметов в базе")
    return len(item_base.items) > 0


@bot.message_handler(commands=['start'])
def welcome_message(message):
    bot.send_message(message.chat.id, "Введите /token <ваш токен>")


@bot.message_handler(commands=['token'])
def token_reading(message):
    if (len(message.text.split()) == 1 or
            check_token(message, message.text.split()[1]) is False):
        return
    bot.send_message(message.chat.id, "Токен введен верно")
    bot.send_message(
        message.chat.id,
        "Добро пожаловать, введите /help, " +
        "чтобы ознакомиться с ботом и его командами")


@bot.message_handler(commands=['help'])
def help_message(message):
    if (check_token(message) is False):
        return
    bot.send_message(
        message.chat.id,
        "Этот бот создан, чтобы парсить https://steamcommunity.com/market/")
    bot.send_message(
        message.chat.id,
        "Список комманд:")
    bot.send_message(
        message.chat.id,
        "/token (hash) установить токен")
    bot.send_message(
        message.chat.id,
        "/random - выберет рандомно элемент из базы и выдаст информацию о нем")
    bot.send_message(
        message.chat.id,
        "/elements (n) - выведет все(n) элементы из базы и информацию о них")
    bot.send_message(
        message.chat.id,
        "/update (n) - введите, чтобы загрузить ~все вещи(n) в базу")
    bot.send_message(
        message.chat.id,
        "/update <name> - введите, чтобы загрузить предмет в базу")
    bot.send_message(
        message.chat.id,
        "P.S. () - обязательные параметры, <> - необязательные параметры")


@bot.message_handler(commands=['update'])
def update(message):
    if (check_token(message) is False):
        return
    print(message.text.split())
    bot.send_message(message.chat.id, "Началось обновление")
    try:
        print(message.text.split()[1])
        pars.parse(int(message.text.split()[1]))
    except:
        pars.parse()
    bot.send_message(message.chat.id, "Обновление прошло успешно")


@bot.message_handler(commands=['random'])
def random_command(message):
    if (check_token(message) is False):
        return
    if (check_base(message) is False):
        return
    position = random.randint(0, config.CNT_ITEMS - 1)
    my_df = pd.DataFrame(
        item_base.items[position:position + 1],
        columns=["name", "url_name", "avg_price", "avg_buys", "last_price"])
    writer = pd.ExcelWriter('items.xlsx')
    my_df.to_excel(writer, 'items')
    writer.save()
    send_doc_file(message.chat.id, 'items.xlsx')


@bot.message_handler(commands=['elements'])
def random_command(message):
    if (check_token(message) is False):
        return
    if (check_base(message) is False):
        return
    lst = message.text.split()
    end_ = len(item_base.items)
    try:
        end_ = int(lst[1])
    except:
        pass
    end_ = min(end_, config.CNT_ITEMS)
    try:
        os.remove('items.csv')
    except OSError:
        pass
    print(100)
    my_df = pd.DataFrame(
        item_base.items[:end_],
        columns=["name", "url_name", "avg_price", "avg_buys", "last_price"])
    writer = pd.ExcelWriter('items.xlsx')
    my_df.to_excel(writer, 'items')
    writer.save()
    send_doc_file(message.chat.id, 'items.xlsx')


@bot.message_handler(commands=['update_item'])
def update_item(message):
    if (len(message.text.split()) < 2):
        bot.send_message(message.chat.id, "Введите название предмета")
        return
    flag = pars.update_item(message.text[13:])
    if (flag is True):
        bot.send_message(message.chat.id, "Предмет успешно добавлен в базу")
    else:
        bot.send_message(message.chat.id, "Предмет не найден")


@bot.message_handler(content_types=['text'])
def repeat_message(message):
    if (check_token(message) is False):
        return
    bot.send_message(message.chat.id, message.text)


bot.polling(none_stop=True)
