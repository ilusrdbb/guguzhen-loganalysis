#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2022/12/16 14:16
# @Author : chaocai
from core import config, util, enemy, battle, sql, attribute, template


def start():
    print('Version 2.8.3')
    # 加载配置文件
    config._init()
    # 加载模板
    template_list = template.init_template()
    # 加载系数缓存数据库文件
    sql.init_db()
    # 解析排行榜
    if config.read_config('is_search_level'):
        enemy.init_top_players()
    # 解析收割机脚本导出文件
    json_data_dict = util.file_load()
    # 权重统计 论坛获取系数 防守记录分析
    w_dict = json_data_dict['w_dict']
    # 删除输出文件
    util.del_file(config.read_config('output_path'))
    # 临时存储战斗数据，防止重复分析影响性能
    battle_map = {}
    for cache_enemy_data in json_data_dict['enemy_list']:
        battle_map[cache_enemy_data.enemy_name] = cache_enemy_data
    # 最终分析结果
    result_dict = {}
    for enemy_name in battle_map:
        enemy_data = battle_map.get(enemy_name)
        # 争夺等级
        enemy_data.kf_level = w_dict.get(enemy_data.enemy_name).get('kf_level')
        # 初始化战斗数据
        battle_data = battle.Battle(enemy_data.battle_log)
        # 获取护符
        aumlet_str = build_aumlet_str(enemy_data.enemy_card, battle_data.gear_list[0])
        # 模板匹配
        match_template = template.match_template(template_list, enemy_data, battle_data)
        if match_template:
            attr_data = attribute.Attribute(None)
            template.build_template_attr(match_template, attr_data)
        else:
            # 初始化点数
            attr_data = attribute.Attribute(enemy_data)
            # 点数推断
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
        util.move_element_to_end(result_dict, enemy_data.enemy_name)
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


