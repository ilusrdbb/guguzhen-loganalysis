#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2022/12/16 14:16
# @Author : chaocai
import datetime
import time

from core import config, util, enemy, battle, sql, attribute


def start():
    # 加载配置文件
    config._init()
    # 加载系数缓存数据库文件
    sql.init_db()
    # 解析排行榜
    if config.read_config('is_search_level'):
        enemy.init_top_players()
    # 解析json
    json_data = util.file_load()
    # 权重统计 论坛获取系数 防守记录分析
    w_dict = get_w_dict(json_data)
    # 删除输出文件
    util.del_file(config.read_config('output_path'))
    # 利用dict的特性新的覆盖旧的
    result_dict = {}
    for data in json_data:
        # 排除野怪结果
        if data['char'] == '野怪':
            continue
        # 防守记录跳过
        if data.get('type') == 'defense':
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
        # 争夺等级
        if w_dict.get(enemy_data.enemy_name) and w_dict.get(enemy_data.enemy_name).get('kf_level'):
            enemy_data.kf_level = w_dict.get(enemy_data.enemy_name).get('kf_level')
        # 初始化战斗数据
        battle_data = battle.Battle(enemy_data.battle_log)
        # 初始化点数
        attr_data = attribute.Attribute(enemy_data)
        # 点数推断
        aumlet_str = build_aumlet_str(enemy_data.enemy_card, battle_data.gear_list[0])
        attribute.cal_attr(enemy_data, battle_data, attr_data, aumlet_str)
        result_list = []
        # 构造角色
        result_list.append(build_first_line(enemy_data, w_dict))
        # 构造许愿池
        result_list.append(build_second_line())
        # 构造护符
        result_list.append(build_third_line(aumlet_str))
        # 构造六围
        result_list.append(build_four_line(attr_data))
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
    # 输出
    util.write_data(result_dict)


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
def build_four_line(attr_data):
    return str(attr_data.t_str) + ' ' + str(attr_data.t_agi) + ' ' + \
           str(attr_data.t_int) + ' ' + str(attr_data.t_vit) + ' ' + \
           str(attr_data.t_spr) + ' ' + str(attr_data.t_mnd)


# 构造第9行
def build_last_line(talent_list):
    return str(len(talent_list)) + ' ' + ' '.join(talent_list)


# 构造第一行
def build_first_line(enemy_data, w_dict):
    enemy_card = enemy_data.enemy_card
    enemy_name = enemy_data.enemy_name
    w_str = ''
    if config.read_config('is_add_w'):
        w_str = 'W=' + str(w_dict[enemy_name]['weight']) + ' '
    if enemy_card == 'YA':
        return w_str + enemy_card + '_' + enemy_data.enemy_name + ' M=' + str(enemy_data.ya_mode) \
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


# 获取护符字符串
def build_aumlet_str(enemy_card, weapon):
    if config.read_config('amulet_config').get(enemy_card + '_' + weapon):
        aumlet = config.read_config('amulet_config').get(enemy_card + '_' + weapon)
    elif config.read_config('amulet_config').get(enemy_card):
        aumlet = config.read_config('amulet_config').get(enemy_card)
    else:
        aumlet = config.read_config('amulet_config')['default']
    return aumlet


# 构造第三行
def build_third_line(aumlet):
    return 'AMULET ' + aumlet + ' ENDAMULET'


def get_w_dict(json_data):
    result_map = {}
    for data in json_data:
        # 排除野怪结果
        if data['char'] == '野怪':
            continue
        # 防守记录跳过
        if data.get('type') == 'defense':
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
        if data['enemyname'] in result_map:
            result_map[data['enemyname']]['weight'] += 1
        else:
            enemy_data = {'enemy_name': data['enemyname'],
                          'enemy_card': config.read_config('card_map').get(data['char']),
                          'weight': 1}
            if config.read_config('is_search_level') and config.read_config('cookie') and int(data['charlevel']) == 850:
                # 通过论坛发帖获取真实的系数
                enemy_data['kf_level'] = enemy.get_kf_level(data['enemyname'])
            result_map[data['enemyname']] = enemy_data
    # 防守记录分析
    if config.read_config('is_analyse_defense'):
        for data in json_data:
            if data.get('type') == 'defense':
                defense_name = data['enemyname']
                defense_card =  config.read_config('card_map').get(data['char'])
                # 获取匹配数据
                match_name = match_defense_name(defense_name, defense_card, result_map)
                if match_name:
                    result_map[match_name]['weight'] += 1
    return result_map


# 防守数据匹配进攻数据
def match_defense_name(defense_name, defense_card, result_map):
    # 名称与卡片匹配
    if result_map.get(defense_name) and result_map.get(defense_name).get('enemy_card'):
        return defense_name
    # 不匹配匹配进攻记录最高系数的同卡片记录
    match_list = []
    for enemy_name in result_map:
        if result_map[enemy_name].get('kf_level') and result_map[enemy_name]['enemy_card'] == defense_card:
            match_list.append(result_map[enemy_name])
    if match_list:
        # 系数从大到小排序
        return sorted(match_list, key=lambda x: x['kf_level'], reverse=True)[0]['enemy_name']
    return None


