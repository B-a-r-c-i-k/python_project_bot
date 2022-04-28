import config
import ujson as json
import requests
import time
import numpy as np
import pandas as pd
import item_base
import os

GAMEID = config.game_id["cs:go"]


def get_cnt_items():
    cnt_items = json.loads(requests.get(
        'https://steamcommunity.com/market/search/render/?search_descriptions=0&sort_column=default&sort_dir=desc&appid=' +
        GAMEID + '&norender=1&count=100',
        cookies=config.cookie).content)['total_count']
    return cnt_items


def get_names(part_info_items):
    part_info_items = json.loads(part_info_items.content)['results']
    names = np.array([])
    for item in part_info_items:
        names = np.append(names, item['hash_name'])
    return names


def get_correct_form(names):
    for i in range(len(names)):
        names[i] = names[i].replace(' ', '%20')
        names[i] = names[i].replace('&', '%26')
        names[i] = names[i].replace('(', '%28')
        names[i] = names[i].replace(')', '%29')
        names[i] = names[i].replace('|', '%7C')
    # return names


def processing(prices_info):
    prices_info = prices_info[::-1]
    cnt = 0
    days = 0
    cash = 0
    last_day = -1
    for trio in prices_info:
        if (trio[0][10] == '0'):
            break
        cnt += int(trio[2])
        cash += trio[1]
        if (int(trio[0][4]) * 10 + int(trio[0][5]) != last_day):
            days += 1
            last_day = int(trio[0][4]) * 10 + int(trio[0][5])
    return np.array([cash / days, cnt / days, prices_info[0][1]])


def update_item(name):
    item_info = np.array([name])
    name = [name]
    get_correct_form(name)
    item_info = np.append(item_info, name[0])
    try:
        j = json.loads(
            requests.get(
                'https://steamcommunity.com/market/pricehistory/?appid=' +
                GAMEID + '&market_hash_name=' + name[0],
                cookies=config.cookie).content)
        if j["success"] is not True:
            return False
        item_info = np.concatenate([item_info, processing(j["prices"])])
        for i in range(len(item_base.items)):
            if (item_base.items[i][0] == item_info[0]):
                item_base.items = np.delete(item_base.items, i, axis=0)
                break
        if (len(item_base.items) != 0):
            item_base.items = np.ravel(item_base.items)
        item_info = np.ravel(item_info)
        if (len(item_base.items) != 0):
            item_base.items = np.concatenate([item_base.items, item_info])
            item_base.items = item_base.items.reshape(
                len(item_base.items) // 5, 5)
        else:
            item_base.items = item_info.reshape(1, 5)
        return True
    except:
        return False


def parse(cnt=None):
    if ((cnt is not None) and (cnt < 0)):
        return
    cnt_items = cnt
    if (cnt is None):
        cnt_items = get_cnt_items()
    config.CNT_ITEMS = cnt_items
    names = np.array([])
    for position in range(0, cnt_items, 100):
        print(position)
        time.sleep(0.5)
        part_info_items = requests.get(
            'https://steamcommunity.com/market/search/render/?start=' +
            str(position) +
            '&count=10&search_descriptions=0&sort_column=default&sort_dir=desc&appid=' +
            GAMEID + '&norender=1&count=500', cookies=config.cookie)
        names = np.concatenate([names, get_names(part_info_items)])
    list_for_print = np.array([])
    names = list(set(names))
    correct_names = names[:]
    get_correct_form(names)
    position = 0
    for name in names:
        if (position == cnt_items):
            break
        print(position)
        list_for_print = np.append(list_for_print, correct_names[position])
        list_for_print = np.append(list_for_print, name)
        j = json.loads(requests.get(
            'https://steamcommunity.com/market/pricehistory/?appid=' +
            GAMEID + '&market_hash_name=' + name,
            cookies=config.cookie).content)["prices"]
        list_for_print = np.concatenate(
            [list_for_print,
             processing(j)])
        position += 1
    item_base.items = list_for_print.reshape(len(list_for_print) // 5, 5)
