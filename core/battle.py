# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/3/29 10:28
# @Author : chaocai

import re

from lxml import html

from core import config


class Battle:
    # 卡片六围点数
    attr_list = []
    # 天赋
    talent_list = []
    # 装备
    gear_list = []
    # 装备等级
    gear_level_list = []
    # 装备是否神秘 0否1是
    gear_mystery_list = []

    # 初始化战斗数据
    def __init__(self, battle_log):
        # 解析html
        battle_log_dom = html.fromstring(battle_log)
        self.attr_list = self.get_attr_list(battle_log_dom)
        self.talent_list = self.get_talent_list(battle_log_dom)
        self.gear_list = self.get_gear_list(battle_log_dom)
        self.gear_level_list = self.get_gear_level_list(battle_log_dom)
        self.gear_mystery_list = self.get_gear_mystery_list(battle_log_dom, self.gear_list)

    # 获取装备神秘
    def get_gear_mystery_list(self, battle_log_dom, gear_list):
        result_list = []
        color_list = [int(re.findall(config.read_config('match_config')['color'], battle_log_dom.xpath(config.read_config('xpath_config')['color'])[4])[0][-1]),
                      int(re.findall(config.read_config('match_config')['color'], battle_log_dom.xpath(config.read_config('xpath_config')['color'])[5])[0][-1]),
                      int(re.findall(config.read_config('match_config')['color'], battle_log_dom.xpath(config.read_config('xpath_config')['color'])[6])[0][-1]),
                      int(re.findall(config.read_config('match_config')['color'], battle_log_dom.xpath(config.read_config('xpath_config')['color'])[7])[0][-1])]
        for i in range(0, len(gear_list)):
            gear = gear_list[i]
            color = color_list[i]
            if gear in config.read_config('default_gear_mystery'):
                result_list.append('1')
            elif color == 5:
                result_list.append('1')
            else:
                result_list.append('0')
        return result_list

    # 获取装备等级list
    def get_gear_level_list(self, battle_log_dom):
        return [battle_log_dom.xpath(config.read_config('xpath_config')['level'])[4],
                battle_log_dom.xpath(config.read_config('xpath_config')['level'])[5],
                battle_log_dom.xpath(config.read_config('xpath_config')['level'])[6],
                battle_log_dom.xpath(config.read_config('xpath_config')['level'])[7]]

    # 获取装备list
    def get_gear_list(self, battle_log_dom):
        return [config.read_config('gear_map')[battle_log_dom.xpath(config.read_config('xpath_config')['gear'])[4]],
                config.read_config('gear_map')[battle_log_dom.xpath(config.read_config('xpath_config')['gear'])[5]],
                config.read_config('gear_map')[battle_log_dom.xpath(config.read_config('xpath_config')['gear'])[6]],
                config.read_config('gear_map')[battle_log_dom.xpath(config.read_config('xpath_config')['gear'])[7]]]

    # 获取六围list
    def get_attr_list(self, battle_log_dom):
        attr_str = battle_log_dom.xpath(config.read_config('xpath_config')['attr'])[2]
        return [str(int(re.findall(config.read_config('match_config')['str'], attr_str)[0])),
                str(int(re.findall(config.read_config('match_config')['agi'], attr_str)[0])),
                str(int(re.findall(config.read_config('match_config')['int'], attr_str)[0])),
                str(int(re.findall(config.read_config('match_config')['vit'], attr_str)[0])),
                str(int(re.findall(config.read_config('match_config')['spr'], attr_str)[0])),
                str(int(re.findall(config.read_config('match_config')['mnd'], attr_str)[0]))]

    # 获取天赋list
    def get_talent_list(self, battle_log_dom):
        talent_str = ''.join(battle_log_dom.xpath(config.read_config('xpath_config')['talent']))
        result_list = []
        talent_list = re.findall(config.read_config('match_config')['talent'], talent_str)
        for talent in talent_list:
            talent = talent.replace('|', '').replace('<br>', '')
            if talent:
                result_list.append(config.read_config('talent_map')[talent])
        return result_list
