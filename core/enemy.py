#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/3/29 10:28
# @Author : chaocai

from core import config


class Enemy:
    # 用户名
    enemy_name = None
    # 卡片等级
    card_level = None
    # 争夺等级
    kf_level = None
    # 战斗记录时间，时间戳
    battle_timestamp = None
    # 卡片
    enemy_card = None
    # 成长值
    card_g = None
    # 技能位
    skill_num = 7
    # 品质
    card_quality = 11
    # 战斗记录
    battle_log = None
    # 雅的模式 0白天1黑夜2凶神
    ya_mode = 0

    # 初始化对手数据
    def __init__(self, data):
        self.card_g = config.read_config('default_g')
        self.enemy_name = data['enemyname']
        self.card_level = int(data['charlevel'])
        if self.card_level == 850:
            self.kf_level = config.read_config('max_kf_level')
        else:
            self.kf_level = self.card_level - 200
        self.battle_timestamp = data['time']
        self.enemy_card = config.read_config('card_map').get(data['char'])
        self.ya_mode = config.read_config('ya_mode')
        if self.enemy_card == 'YA2':
            self.enemy_card = 'YA'
            self.ya_mode = 2
        self.battle_log = data['log']