#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2022/12/16 14:16
# @Author : chaocai
import datetime
import json
import os
import time

from config import *
from core import attribute, talent


def start():
    # 解析json，并按照时间排序
    json_data = sorted(load_data(), key=lambda x: (x['time']))
    # 删除输出文件
    delFile(OUTPUT_PATH)
    result_map = {}
    for data in json_data:
        enemy_name = data['enemyname']
        enemy_level = int(data['charlevel'])
        battle_timestamp = data['time']
        enemy_card = CARD_MAP[data['char']]
        battle_log_str = data['log']
        # 白名单
        if WHITE_LIST and enemy_name not in WHITE_LIST:
            continue
        # 黑名单跳过
        if BLACK_LIST and enemy_name in BLACK_LIST:
            continue
        # 等级跳过
        if MIN_LEVEL and enemy_level < MIN_LEVEL:
            continue
        # 日期跳过
        if LAST_DATE:
            last_datetime = datetime.datetime.strptime(LAST_DATE + ' 00:00:00.000', "%Y-%m-%d %H:%M:%S.%f")
            last_timestamp = int(time.mktime(last_datetime.timetuple()) * 1000.0 + last_datetime.microsecond / 1000.0)
            if last_timestamp > battle_timestamp:
                continue
        result_list = []
        # 构造第一行
        result_list.append(build_first_line(enemy_card, enemy_name))
        # 构造第二行
        result_list.append(build_second_line())
        # 构造天赋list
        talent_list = talent.get_talent_list(battle_log_str)
        # 构造第三行
        result_list.append(build_third_line(talent_list))
        # 构造属性map
        attribute_map = attribute.get_attribute_map(battle_log_str, talent_list, enemy_level)
        # 构造4 5 6 7 8行
        result_list.append(build_four_line(attribute_map))
        result_list.append(build_five_line(attribute_map))
        result_list.append(build_six_line(attribute_map))
        result_list.append(build_seven_line(attribute_map))
        result_list.append(build_eight_line(attribute_map))
        # 构造9行
        result_list.append(build_last_line(talent_list, attribute_map['gear'], enemy_card))
        # 构造map
        result_str = '\n'.join(result_list) + '\n\n'
        result_map[enemy_name] = result_str
    # 输出
    write_data(OUTPUT_PATH, result_map)


# 写入
def write_data(path, result_map):
    print('输出对手数量：%s' % len(result_map))
    for key in result_map:
        str = result_map[key]
        with open(path, 'a', encoding='utf-8') as f:
            f.write(str)


# 删除输出文件
def delFile(path):
    if os.path.isfile(path):
        os.remove(path)


# 构造第8行
def build_eight_line(attribute_map):
    return str(attribute_map['crt']) + ' ' \
           + str(attribute_map['skl']) + ' ' \
           + str(attribute_map['rfl']) + ' ' \
           + str(attribute_map['lch'])


# 构造第7行
def build_seven_line(attribute_map):
    return str(attribute_map['hp']) + ' ' \
           + str(attribute_map['hpr']) + ' ' \
           + str(attribute_map['_hpr']) + ' ' \
           + str(attribute_map['sld']) + ' ' \
           + str(attribute_map['sldr']) + ' '\
           + str(attribute_map['_sldr'])


# 构造第6行
def build_six_line(attribute_map):
    return str(attribute_map['spd']) + ' ' \
           + str(attribute_map['pdef']) + ' ' \
           + str(attribute_map['pdec']) + ' ' \
           + str(attribute_map['mdef']) + ' ' \
           + str(attribute_map['mdec'])


# 构造第5行
def build_five_line(attribute_map):
    return str(attribute_map['pth']) + ' ' \
           + str(attribute_map['_pth']) + ' ' \
           + str(attribute_map['mth']) + ' ' \
           + str(attribute_map['_mth']) + ' ' \
           + str(attribute_map['cth'])


# 构造第4行
def build_four_line(attribute_map):
    return str(attribute_map['patk']) + ' ' + str(attribute_map['matk']) + ' 0'


# 构造第9行
def build_last_line(talent_list, gear_list, enemy_card):
    result_list = []
    if gear_list:
        for gear in gear_list:
            # 专属
            if gear == 'DAGGER' and enemy_card == 'AI':
                result_list.append(gear)
            elif gear == 'WAND' and enemy_card == 'MO':
                result_list.append(gear)
            elif gear == 'RIBBON' and enemy_card == 'LIN':
                result_list.append(gear)
            elif gear == 'TIARA' and enemy_card == 'MENG':
                result_list.append(gear)
            elif gear == 'RING' and enemy_card == 'WU':
                result_list.append(gear)
            elif gear == 'DEVOUR' and enemy_card == 'MING':
                result_list.append(gear)
            # 神秘配置
            if gear in DEFULT_SECRET and gear != 'THORN':
                result_list.append(gear)
    if talent_list:
        for talent in talent_list:
            if talent in TALENT_CONFIG:
                result_list.append(talent)
    return str(len(result_list)) + " " + " ".join(result_list)


# 构造第一行
def build_first_line(enemy_card, enemy_name):
    if enemy_card == 'WU':
        return enemy_card + '_' + enemy_name + ' G=' + str(DEFAULT_G) + ' STAT'
    return enemy_card + '_' + enemy_name + ' STAT'


# 构造第二行
def build_second_line():
    return 'WISH ' + DEFAULT_WISH


# 构造第三行
def build_third_line(talent_list):
    if 'XUE' in talent_list:
        return 'AMULET REC 10 ' + DEFAULT_AMULET + ' ENDAMULET'
    return 'AMULET ' + DEFAULT_AMULET + ' ENDAMULET'


# 加载数据
def load_data():
    result_list = []
    for file_name in os.listdir(INPUT_PATH):
        if file_name != 'pc.txt':
            file_path = INPUT_PATH + file_name
            with open(file_path, encoding='utf-8') as f:
                read = f.read()
                try:
                    data_list = json.loads(read)['data']['data'][0]['rows']
                    result_list.extend(data_list)
                except:
                    pass
    return result_list
