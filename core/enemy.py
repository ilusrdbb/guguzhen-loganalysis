#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/3/29 10:28
# @Author : chaocai
from lxml import html

from core import config, util


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


# 通过论坛发帖获取真实的系数
def get_kf_level(enemy_data):
    print('开始获取%s的系数...' % enemy_data.enemy_name)
    # 搜索
    domain = config.read_config('kf_domain')
    search_url = domain + config.read_config('url_config')['search']
    search_param = {
        'step': 2,
        'method': 'AND',
        'sch_area': 0,
        's_type': 'forum',
        'f_fid': 'all',
        'orderway': 'lastpost',
        'asc': 'DESC',
        'keyword': '',
        'pwuser': enemy_data.enemy_name.encode('GB2312')
    }
    search_text = util.http_post(search_url, search_param, '网络错误')
    if search_text:
        search_dom = html.fromstring(search_text)
        if search_dom.xpath(config.read_config('xpath_config')['search']):
            read_url = domain + '/' + search_dom.xpath(config.read_config('xpath_config')['search'])[0]
            read_text = util.http_get(read_url, None, '网络错误')
            if read_text:
                read_dom = html.fromstring(read_text)
                if read_dom.xpath(config.read_config('xpath_config')['read']):
                    uid_url = domain + '/' + read_dom.xpath(config.read_config('xpath_config')['read'])[0]
                    uid_text = util.http_get(uid_url, None, '网络错误')
                    if uid_text:
                        uid_dom = html.fromstring(uid_text)
                        if uid_dom.xpath(config.read_config('xpath_config')['info']):
                            forum_text = uid_dom.xpath(config.read_config('xpath_config')['info'])[5]
                            forum_level = forum_text.replace('神秘系数：', '')
                            if forum_level:
                                # 3s默认svip
                                print('%s的系数获取成功，系数为%s' % (enemy_data.enemy_name, str(int(forum_level))))
                                enemy_data.kf_level = int(forum_level) + config.read_config('shadow_level') + 100
        else:
            print('%s未找到发帖记录' % enemy_data.enemy_name)
