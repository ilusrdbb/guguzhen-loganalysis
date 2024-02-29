#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/9/27 15:44
# @Author : chaocai
from lxml import html

from core import config, util, sql


class Templete:
    # 初始化对手数据
    def __init__(self, data):
        # 用户名
        self.enemy_name = data['enemy']
        # 卡片
        self.enemy_card = data['card']
        # 装备列表
        self.gear_list = data['gear'].split(' ')
        # 箭头列表
        self.attribute_list = data['attribute'].split(' ')
        # 点数
        self.point = data['point']
        point_list = data['point'].split(' ')
        # 总点数
        self.all_point = int(point_list[0]) + int(point_list[1]) + int(point_list[2]) + \
                         int(point_list[3]) + int(point_list[4]) + int(point_list[5])


# 初始化模板
def init_template():
    result_list = []
    template_list = config.read_config('template')
    if template_list:
        for template in template_list:
            result_list.append(Templete(template))
    return result_list


# 匹配模板
def match_template(template_list, enemy_data, battle_data):
    if template_list:
        for template in template_list:
            # 点数校验
            all_point = int((6 + enemy_data.card_level * 3) * (100 + enemy_data.card_quality) / 100)
            if all_point < template.all_point:
                continue
            # 玩家名称匹配
            if template.enemy_name and template.enemy_name != enemy_data.enemy_name:
                continue
            # 卡片匹配
            if template.enemy_card and template.enemy_card != enemy_data.enemy_card:
                continue
            # 装配匹配
            match_gear_flag = get_gear_flag(template.gear_list, battle_data.gear_list)
            if not match_gear_flag:
                continue
            # 箭头匹配
            match_attr_flag = get_attr_flag(template.attribute_list, battle_data.attr_list)
            if not match_attr_flag:
                continue
            return template
    return None


# 是否匹配模板装备
def get_gear_flag(template_gear_list, enemy_gear_list):
    for i in range(0, len(template_gear_list)):
        if template_gear_list[i] != 'NONE' and template_gear_list[i] != enemy_gear_list[i]:
            return False
    return True


# 是否匹配箭头
def get_attr_flag(template_attr_list, enemy_attr_list):
    for i in range(0, len(template_attr_list)):
        if template_attr_list[i] != 'any':
            if 'double-angle-down' in enemy_attr_list[i] and template_attr_list[i] != 'dd':
                return False
            if 'icon-angle-down' in enemy_attr_list[i] and template_attr_list[i] != 'd':
                return False
            if 'icon-angle-up' in enemy_attr_list[i] and template_attr_list[i] != 'u':
                return False
            if 'double-angle-up' in enemy_attr_list[i] and template_attr_list[i] != 'du':
                return False
    return True


# 模板点数转属性点
def build_template_attr(templete, attr_data):
    point_list = templete.point.split(' ')
    attr_data.t_str = int(point_list[0])
    attr_data.t_agi = int(point_list[1])
    attr_data.t_int = int(point_list[2])
    attr_data.t_vit = int(point_list[3])
    attr_data.t_spr = int(point_list[4])
    attr_data.t_mnd = int(point_list[5])