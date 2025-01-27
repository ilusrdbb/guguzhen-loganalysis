import this

from core import config


class Gear(object):

    def __init__(self, attr_list, talent_list, enemy_card):
        self.attr_list = attr_list
        self.talent_list = talent_list
        self.enemy_card = enemy_card

    def get_match_gear(self):
        gear_config_list = config.read_gear('template')[self.enemy_card]
        for gear_config in gear_config_list:
            match_mode = gear_config.get('mode')
            if not match_mode:
                # 默认add模式
                match_mode = 'add'
            match_flag = False
            match_talent_list = gear_config.get('talent')
            match_attr_list = gear_config.get('attribute')
            if not match_attr_list and not match_talent_list:
                # 未配置点数和光环直接算作匹配上
                return gear_config['gear']
            if match_talent_list:
                for match_talent in match_talent_list:
                    if match_mode == 'add':
                        # add模式 有一个未匹配上就算不通过
                        if match_talent not in self.talent_list:
                            match_flag = False
                            break
                        match_flag = True
                    if match_mode == 'or':
                        # or模式 有一个能匹配上就算通过
                        if match_talent in self.talent_list:
                            match_flag = True
                            break
                # 未通过光环校验
                if not match_flag:
                    continue
            if match_attr_list:
                for match_attr in match_attr_list:
                    if match_mode == 'add':
                        # add模式 有一个未匹配上就算不通过
                        if not self.match_attr(match_attr.split(':')[0], match_attr.split(':')[1], self.attr_list):
                            match_flag = False
                            break
                        match_flag = True
                    if match_mode == 'or':
                        # or模式 有一个能匹配上就算通过
                        if self.match_attr(match_attr.split(':')[0], match_attr.split(':')[1], self.attr_list):
                            match_flag = True
                            break
                # 未通过点数校验
                if not match_flag:
                    continue
            return gear_config['gear']
        # 没有模板匹配则按照全部配置中的第一个模板配置
        return gear_config_list[0]['gear']

    def match_attr(self, match_attr, match_icon, attr_list):
        # 获取配置属性对应的实际箭头
        attr_icon = ''
        if match_attr == 'STR':
            attr_icon = self.convert_icon(attr_list[0])
        if match_attr == 'AGI':
            attr_icon = self.convert_icon(attr_list[1])
        if match_attr == 'INT':
            attr_icon = self.convert_icon(attr_list[2])
        if match_attr == 'VIT':
            attr_icon = self.convert_icon(attr_list[3])
        if match_attr == 'SPR':
            attr_icon = self.convert_icon(attr_list[4])
        if match_attr == 'MND':
            attr_icon = self.convert_icon(attr_list[5])
        if match_icon == attr_icon:
            return True
        return False

    def convert_icon(self, icon):
        if 'double-angle-up' in icon:
            return 'du'
        if 'double-angle-down' in icon:
            return 'dd'
        if 'icon-angle-up' in icon:
            return 'u'
        if 'icon-angle-down' in icon:
            return 'd'
        return ''
