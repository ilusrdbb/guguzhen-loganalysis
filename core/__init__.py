#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2022/12/16 14:16
# @Author : chaocai
import datetime
import time
from collections import Counter

from core import config, file, enemy, battle


def start():
    # 加载配置文件
    config._init()
    # 解析json
    json_data = file.file_load()
    # 权重统计
    w_map = get_w_map(json_data);
    # 删除输出文件
    file.del_file(config.read_config('output_path'))
    # 利用dict的特性新的覆盖旧的
    result_dict = {}
    level_dict = {}
    for data in json_data:
        # 排除野怪结果
        if data['char'] == '野怪':
            continue
        # 初始化对手数据
        enemy_data = enemy.Enemy(data)
        # 白名单
        if config.read_config('white_list') and enemy_data.enemy_name not in config.read_config('white_list'):
            continue
        # 黑名单跳过
        if config.read_config('black_list') and enemy_data.enemy_name in config.read_config('black_list'):
            continue
        # 等级跳过
        if config.read_config('min_card_level') and enemy_data.card_level < config.read_config('min_card_level'):
            continue
        # 日期跳过
        if config.read_config('last_date'):
            last_datetime = datetime.datetime.strptime(config.read_config('last_date') + ' 00:00:00.000',
                                                       "%Y-%m-%d %H:%M:%S.%f")
            last_timestamp = int(time.mktime(last_datetime.timetuple()) * 1000.0 + last_datetime.microsecond / 1000.0)
            if last_timestamp > enemy_data.battle_timestamp:
                continue
        # 获取争夺等级
        if result_dict.get(enemy_data.enemy_name):
            enemy_data.kf_level = result_dict.get(enemy_data.enemy_name)
        else:
            if config.read_config('is_search_level') and config.read_config('cookie'):
                # 通过论坛发帖获取真实的系数
                enemy.get_kf_level(enemy_data)
        # 初始化战斗数据
        battle_data = battle.Battle(enemy_data.battle_log)
        result_list = []
        # 构造角色
        result_list.append(build_first_line(enemy_data, w_map))
        # 构造许愿池
        result_list.append(build_second_line())
        # 构造护符
        result_list.append(build_third_line(enemy_data.enemy_card, battle_data.gear_list[0]))
        # 构造六围
        result_list.append(build_four_line(battle_data.attr_list))
        # 构造装备
        result_list.append(build_five_line(battle_data))
        result_list.append(build_six_line(battle_data))
        result_list.append(build_seven_line(battle_data))
        result_list.append(build_eight_line(battle_data))
        # 构造天赋
        result_list.append(build_last_line(battle_data.talent_list))
        # 构造map
        result_str = '\n'.join(result_list) + '\n\n'
        result_dict[enemy_data.enemy_name] = result_str
        level_dict[enemy_data.enemy_name] = enemy_data.kf_level
    # 输出
    file.write_data(result_dict)


# 构造第8行
def build_eight_line(battle_data):
    return battle_data.gear_list[3] + ' ' \
           + battle_data.gear_level_list[3] + ' ' \
           + config.read_config('gear_config')[battle_data.gear_list[3]] + ' ' \
           + battle_data.gear_mystery_list[3]


# 构造第7行
def build_seven_line(battle_data):
    return battle_data.gear_list[2] + ' ' \
           + battle_data.gear_level_list[2] + ' ' \
           + config.read_config('gear_config')[battle_data.gear_list[2]] + ' ' \
           + battle_data.gear_mystery_list[2]


# 构造第6行
def build_six_line(battle_data):
    return battle_data.gear_list[1] + ' ' \
           + battle_data.gear_level_list[1] + ' ' \
           + config.read_config('gear_config')[battle_data.gear_list[1]] + ' ' \
           + battle_data.gear_mystery_list[1]


# 构造第5行
def build_five_line(battle_data):
    return battle_data.gear_list[0] + ' ' \
        + battle_data.gear_level_list[0] + ' ' \
        + config.read_config('gear_config')[battle_data.gear_list[0]] + ' ' \
        + battle_data.gear_mystery_list[0]


# 构造第4行
def build_four_line(attr_list):
    return ' '.join(attr_list)


# 构造第9行
def build_last_line(talent_list):
    return str(len(talent_list)) + ' ' + ' '.join(talent_list)


# 构造第一行
def build_first_line(enemy_data, w_map):
    enemy_card = enemy_data.enemy_card
    enemy_name = enemy_data.enemy_name
    w_str = ''
    if config.read_config('is_add_w'):
        w_str = 'W=' + str(w_map[enemy_name]) + ' '
    if enemy_card == 'YA':
        return enemy_card + '_' + enemy_data.enemy_name + ' M=' + str(enemy_data.ya_mode) \
               + ' ' + str(enemy_data.card_level) \
               + ' ' + str(enemy_data.kf_level) \
               + ' ' + str(enemy_data.skill_num) \
               + ' ' + str(enemy_data.card_quality)
    elif enemy_card == 'WU' or enemy_card == 'XI' or enemy_card == 'XIA':
        return w_str + enemy_card + '_' + enemy_data.enemy_name + ' G=' + str(enemy_data.card_g) \
               + ' ' + str(enemy_data.card_level) \
               + ' ' + str(enemy_data.kf_level) \
               + ' ' + str(enemy_data.skill_num) \
               + ' ' + str(enemy_data.card_quality)
    return w_str + enemy_card + '_' + enemy_data.enemy_name \
           + ' ' + str(enemy_data.card_level) \
           + ' ' + str(enemy_data.kf_level) \
           + ' ' + str(enemy_data.skill_num) \
           + ' ' + str(enemy_data.card_quality)


# 构造第二行
def build_second_line():
    return 'WISH ' + config.read_config('wish_config')


# 构造第三行
def build_third_line(enemy_card, weapon):
    if config.read_config('amulet_config').get(enemy_card + '_' + weapon):
        aumlet = config.read_config('amulet_config').get(enemy_card + '_' + weapon)
    elif config.read_config('amulet_config').get(enemy_card):
        aumlet = config.read_config('amulet_config').get(enemy_card)
    else:
        aumlet = config.read_config('amulet_config')['default']
    return 'AMULET ' + aumlet + ' ENDAMULET'

# 统计
def get_w_map(json_data):
    result_map = {}
    for data in json_data:
        # 排除野怪结果
        if data['char'] == '野怪':
            continue
        # 白名单
        if config.read_config('white_list') and data['enemyname'] not in config.read_config('white_list'):
            continue
        # 黑名单跳过
        if config.read_config('black_list') and data['enemyname'] in config.read_config('black_list'):
            continue
        # 等级跳过
        if config.read_config('min_card_level') and int(data['charlevel']) < config.read_config('min_card_level'):
            continue
        # 日期跳过
        if config.read_config('last_date'):
            last_datetime = datetime.datetime.strptime(config.read_config('last_date') + ' 00:00:00.000',
                                                       "%Y-%m-%d %H:%M:%S.%f")
            last_timestamp = int(
                time.mktime(last_datetime.timetuple()) * 1000.0 + last_datetime.microsecond / 1000.0)
            if last_timestamp > data['time']:
                continue
        # 计数
        if data["enemyname"] in result_map:
            result_map[data["enemyname"]] += 1
        else:
            result_map[data["enemyname"]] = 1
    return Counter(result_map)
