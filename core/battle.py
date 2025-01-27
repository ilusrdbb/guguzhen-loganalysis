# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/3/29 10:28
# @Author : chaocai

import re

from lxml import html

from core import config
from core.gear import Gear


class Battle:
    # 初始化
    def __init__(self, battle_log, enemy_card):
        super().__init__()
        # 解析html
        battle_log_dom = html.fromstring(battle_log)
        # 卡片六围比例图标
        self.attr_list = self.get_attr_list(battle_log_dom)
        # 对手天赋
        self.talent_list = self.get_talent_list(battle_log_dom)
        # 自身天赋
        self.my_talent_list = self.get_my_talent_list(battle_log_dom)
        # 装备
        self.gear_list = self.get_gear_list(battle_log_dom, self.attr_list, self.talent_list, enemy_card)
        # 装备等级
        self.gear_level_list = self.get_gear_level_list(battle_log_dom)
        # 装备是否神秘 0否1是
        self.gear_mystery_list = self.get_gear_mystery_list(battle_log_dom, self.gear_list)
        # 对手最大生命
        self.hp = int(battle_log_dom.xpath(config.read_config('xpath_config')['hp'])[0].replace('生命', ''))
        # 对手最大护盾
        self.sld = int(battle_log_dom.xpath(config.read_config('xpath_config')['sld'])[0].replace('护盾', ''))
        # 对手第一次出手的物伤
        self.p_damage = None
        # 对手第一次出手的魔伤
        self.m_damage = None
        # 对手第一次出手是否暴击
        self.crt_flag = False
        # 对手第一次出手是否发动技能
        self.skl_flag = False
        # 舞成长值
        self.wu_flag = 0
        # 琳是否触发底力
        self.lin_flag = False
        # 手环是否触发神秘
        self.m_crt_flag = False
        # 自身最大生命，用于计算薇被动
        self.my_max_hp = 0
        # 自身最大护盾，用于计算薇被动
        self.my_max_sld = 0
        # 对手第一次出手前自身生命，用于计算神秘枪魔伤
        self.my_turn_hp = 0
        # 对手第一次出手前自身护盾，用于计算神秘弓物伤
        self.my_turn_sld = 0
        # 对手第一次出手的回合数，用于计算后发的增伤
        self.turn_num = 0
        # 是否装备神秘斗篷，用于计算伤害转换
        self.is_cape = False
        # 自身卡片，用于判断是否触发黑夜雅降攻
        self.my_card = None
        # 缓存基础物攻，用于琳的魔伤计算
        self.cache_p_atk = 0
        # 缓存计算到斗篷时需要转换的物伤
        self.cache_p_damage = 0
        # 解析战斗记录
        if config.read_config('is_analyse_battle'):
            # 神秘斗篷判断
            self.is_cape = config.read_gear('is_mystery_cape')
            # 自身卡片
            self.my_card = self.get_my_card(battle_log_dom.xpath(config.read_config('xpath_config')['mycard'])[0])
            # 自身生命护盾
            self.my_turn_hp = int(battle_log_dom.xpath(config.read_config('xpath_config')['myhp'])[0].replace('生命', ''))
            self.my_turn_sld = int(battle_log_dom.xpath(config.read_config('xpath_config')['mysld'])[0].replace('护盾', ''))
            self.my_max_hp = self.my_turn_hp
            self.my_max_sld = self.my_turn_sld
            turn_num = 1
            all_turn_list = battle_log_dom.xpath('./div')
            my_latest_turn = None
            enemy_turn = None
            if all_turn_list:
                for turn_node in all_turn_list:
                    if 'fyg_pvero' in str(turn_node.attrib):
                        if 'hl-info' in str(turn_node.attrib):
                            enemy_turn = html.fromstring(html.tostring(turn_node))
                            break
                        my_latest_turn = html.fromstring(html.tostring(turn_node))
                        turn_num += 1
            if enemy_turn is None:
                self.turn_num = 0
            else:
                # 对手第一次出手前的回合
                if my_latest_turn is not None:
                    my_text_list = my_latest_turn.xpath('./div[1]//text()')
                    my_turn_numbers = [string for string in my_text_list if re.compile(r'\d+').match(string)]
                    self.my_turn_hp = int(my_turn_numbers[-1])
                    self.my_turn_sld = int(my_turn_numbers[-2])
                # 对手第一次出手的回合
                turn_text_list = enemy_turn.xpath('./div[2]//text()')
                if turn_text_list:
                    for turn_text in turn_text_list:
                        if '锦上添花' in turn_text:
                            self.skl_flag = True
                            self.wu_flag = int(re.findall(r'\d+', turn_text)[0])
                        if '底力爆发' in turn_text:
                            self.lin_flag = True
                        if '魔力压制' in turn_text or '爆裂双刃' in turn_text or '烈焰宝石' in turn_text \
                                or '星轮逆转' in turn_text or '终极时刻' in turn_text or '黑发海洋' in turn_text \
                                or '幽梦棱镜' in turn_text or '猩红一怒' in turn_text or '蓝焰侵灼' in turn_text \
                                or '生命掠夺' in turn_text or '鲜血支配' in turn_text:
                            self.skl_flag = True
                        if '暴击' in turn_text_list:
                            self.crt_flag = True
                        if '深蓝冲击' in turn_text:
                            self.m_crt_flag = True
                    turn_numbers = [string for string in turn_text_list if re.compile(r'\d+').match(string)]
                    self.p_damage = int(turn_numbers[0])
                    self.m_damage = int(turn_numbers[1])

    # 获取装备神秘
    @classmethod
    def get_gear_mystery_list(cls, battle_log_dom, gear_list):
        result_list = []
        try:
            color_list = [int(re.findall(config.read_config('match_config')['color'],
                                         battle_log_dom.xpath(config.read_config('xpath_config')['color'])[4])[0][-1]),
                          int(re.findall(config.read_config('match_config')['color'],
                                         battle_log_dom.xpath(config.read_config('xpath_config')['color'])[5])[0][-1]),
                          int(re.findall(config.read_config('match_config')['color'],
                                         battle_log_dom.xpath(config.read_config('xpath_config')['color'])[6])[0][-1]),
                          int(re.findall(config.read_config('match_config')['color'],
                                         battle_log_dom.xpath(config.read_config('xpath_config')['color'])[7])[0][-1])]
        except:
            color_list = [0, 0, 0, 0]
        for i in range(0, len(gear_list)):
            gear = gear_list[i]
            color = color_list[i]
            if gear in config.read_gear('default_gear_mystery'):
                result_list.append('1')
            elif color == 5:
                result_list.append('1')
            elif config.read_gear('all_mystery'):
                result_list.append('1')
            else:
                result_list.append('0')
        return result_list

    # 获取装备等级list
    @classmethod
    def get_gear_level_list(cls, battle_log_dom):
        try:
            return [battle_log_dom.xpath(config.read_config('xpath_config')['level'])[4],
                    battle_log_dom.xpath(config.read_config('xpath_config')['level'])[5],
                    battle_log_dom.xpath(config.read_config('xpath_config')['level'])[6],
                    battle_log_dom.xpath(config.read_config('xpath_config')['level'])[7]]
        except:
            return [str(config.read_gear('gear_level')),
                    str(config.read_gear('gear_level')),
                    str(config.read_gear('gear_level')),
                    str(config.read_gear('gear_level'))]

    # 获取装备list
    @classmethod
    def get_gear_list(cls, battle_log_dom, attr_list, talent_list, enemy_card):
        try:
            return [config.read_gear('gear_map')[battle_log_dom.xpath(config.read_config('xpath_config')['gear'])[4]],
                    config.read_gear('gear_map')[battle_log_dom.xpath(config.read_config('xpath_config')['gear'])[5]],
                    config.read_gear('gear_map')[battle_log_dom.xpath(config.read_config('xpath_config')['gear'])[6]],
                    config.read_gear('gear_map')[battle_log_dom.xpath(config.read_config('xpath_config')['gear'])[7]]]
        except:
            # 模板匹配
            return Gear(attr_list, talent_list, enemy_card).get_match_gear()

    # 获取六围list
    @classmethod
    def get_attr_list(cls, battle_log_dom):
        attr_str = battle_log_dom.xpath(config.read_config('xpath_config')['attr'])[2]
        if len(attr_str) < 3:
            # 新图标
            return [str(item) for item in battle_log_dom.xpath(config.read_config('xpath_config')['attr2'])]
        # 旧点数
        return [re.findall(config.read_config('match_config')['str'], attr_str)[0],
                re.findall(config.read_config('match_config')['agi'], attr_str)[0],
                re.findall(config.read_config('match_config')['int'], attr_str)[0],
                re.findall(config.read_config('match_config')['vit'], attr_str)[0],
                re.findall(config.read_config('match_config')['spr'], attr_str)[0],
                re.findall(config.read_config('match_config')['mnd'], attr_str)[0]]

    # 获取对手天赋list
    @classmethod
    def get_talent_list(cls, battle_log_dom):
        talent_str = ''.join(battle_log_dom.xpath(config.read_config('xpath_config')['talent']))
        result_list = []
        talent_list = re.findall(config.read_config('match_config')['talent'], talent_str)
        for talent in talent_list:
            talent = talent.replace('|', '').replace('<br>', '')
            if talent:
                if talent == '启程之风' or talent == '等级挑战' or talent == '等级压制':
                    continue
                result_list.append(config.read_config('talent_map')[talent])
        return result_list

    # 获取自身天赋list
    @classmethod
    def get_my_talent_list(cls, battle_log_dom):
        talent_str = ''.join(battle_log_dom.xpath(config.read_config('xpath_config')['mytalent']))
        result_list = []
        talent_list = re.findall(config.read_config('match_config')['talent'], talent_str)
        for talent in talent_list:
            talent = talent.replace('|', '').replace('<br>', '')
            if talent:
                result_list.append(config.read_config('talent_map')[talent])
        return result_list

    # 获取自身卡片
    @classmethod
    def get_my_card(cls, card_str):
        if '舞' in card_str:
            return 'WU'
        if '默' in card_str:
            return 'MO'
        if '艾' in card_str:
            return 'AI'
        if '琳' in card_str:
            return 'LIN'
        if '薇' in card_str:
            return 'WEI'
        if '梦' in card_str:
            return 'MENG'
        if '伊' in card_str:
            return 'YI'
        if '冥' in card_str:
            return 'MING'
        if '命' in card_str:
            return 'MIN'
        if '希' in card_str:
            return 'XI'
        if '霞' in card_str:
            return 'XIA'
        if '雅' in card_str:
            return 'YA'
        return ''
