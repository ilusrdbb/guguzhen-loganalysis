#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/3/29 10:28
# @Author : chaocai
from lxml import html

from core import config, util, sql


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
        self.battle_log = data['log']


# 初始化排行榜
def init_top_players():
    print('开始初始化排行榜玩家的系数...')
    domain = config.read_config('kf_domain')
    url = domain + '/kf_no1.php'
    text = util.http_get(url, '', '网络错误')
    if text:
        dom = html.fromstring(text)
        top_list = dom.xpath(config.read_config('xpath_config')['top'])
        for top in top_list:
            name = top.xpath('td//text()')[1]
            level = top.xpath('td//text()')[2].replace('级', '')
            cache_data = sql.query(name)
            if cache_data:
                sql.update(name, level)
            else:
                sql.insert(name, '', level)
        print('初始化排行榜数据成功！')
    else:
        print('获取排行榜数据失败')


# 通过论坛发帖获取真实的系数
def get_kf_level(enemy_name):
    domain = config.read_config('kf_domain')
    cache_data = sql.query(enemy_name)
    if cache_data:
        if config.read_config('use_cache'):
            return int(cache_data[0][2]) + config.read_config('shadow_level') + 100
        else:
            uid_url = domain + '/' + cache_data[0][1]
            print('开始获取%s的系数...' % enemy_name)
            uid_text = util.http_get(uid_url, None, '网络错误')
            if uid_text:
                uid_dom = html.fromstring(uid_text)
                if uid_dom.xpath(config.read_config('xpath_config')['info']):
                    forum_text = uid_dom.xpath(config.read_config('xpath_config')['info'])[5]
                    if '神秘系数' not in forum_text:
                        # 协管需要多读一行
                        forum_text = uid_dom.xpath(config.read_config('xpath_config')['info'])[6]
                    forum_level = forum_text.replace('神秘系数：', '')
                    if forum_level:
                        sql.update(enemy_name, str(int(forum_level)))
                        print('%s的系数获取成功，系数为%s' % (enemy_name, str(int(forum_level))))
                        return int(forum_level) + config.read_config('shadow_level') + 100
    else:
        print('开始获取%s的系数...' % enemy_name)
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
            'pwuser': enemy_name.encode('gbk')
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
                                if '神秘系数' not in forum_text:
                                    # 协管需要多读一行
                                    forum_text = uid_dom.xpath(config.read_config('xpath_config')['info'])[6]
                                forum_level = forum_text.replace('神秘系数：', '')
                                if forum_level:
                                    sql.insert(enemy_name, read_dom.xpath(config.read_config('xpath_config')['read'])[0], str(int(forum_level)))
                                    print('%s的系数获取成功，系数为%s' % (enemy_name, str(int(forum_level))))
                                    return int(forum_level) + config.read_config('shadow_level') + 100
            else:
                # 无发帖记录的扔进数据库中
                forum_level = config.read_config('max_kf_level') - config.read_config('shadow_level') - 100
                sql.insert(enemy_name, '', str(forum_level))
                print('%s未找到发帖记录' % enemy_name)
    return None
