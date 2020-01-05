#!/usr/bin/env python3.7
# coding=utf-8
'''
# 作者: weimo
# 创建日期: 2020-01-04 19:14:32
# 上次编辑时间: 2020-01-05 14:46:27
# 一个人的命运啊,当然要靠自我奋斗,但是...
'''

from datetime import datetime
from random import randint, choice

class ASS(object):

    def __init__(self, file_path, get_xy_obj, font="微软雅黑"):
        self.font = font
        self.get_xy_obj = get_xy_obj
        
        # 起点位置可以随机在一个区域出现
        # 起点位置可以随机在一个区域出现 其他扩展
        self.baseline = """Dialogue: 0,{start_time},{end_time},{font},,0,0,0,,{{{move_text}{color}}}{text}"""
        self.lines = []

    def create_new_line(self, comment):
        text, color, timepoint = comment
        start_time, end_time, show_time = self.set_start_end_time(timepoint)
        font = self.set_random_font(line="")
        move_text = self.set_start_end_pos(text, show_time)
        color = self.set_color(color)
        line = self.baseline.format(start_time=start_time, end_time=end_time, font=font, move_text=move_text, color=color, text=text)
        self.lines.append(line)

    def set_color(self, color: list):
        # \1c&FDA742&
        if color.__len__() == 1:
            color = "\\1c&{}&".format(color[0].lstrip("#").upper())
        else:
            color = "\\1c&{}&".format(choice(color).lstrip("#").upper())
            # color = "\\1c&{}&\\t(0,10000,\\2c&{}&".format(color[0].lstrip("#").upper(), color[1].lstrip("#").upper())
        return color

    def set_start_end_pos(self, text, show_time):
        # 考虑不同大小字体下的情况 TODO
        # \move(1920,600,360,600)
        # min_index = self.get_min_length_used_y()
        start_x = 1920
        width, height, start_y = self.get_xy_obj.get_xy(text, show_time)
        # start_y = self.all_start_y[min_index]
        end_x = -(width + randint(0, 30))
        end_y = start_y
        move_text = "\\move({},{},{},{})".format(start_x, start_y, end_x, end_y)
        # self.update_length_used_y(min_index, text.__len__() * 2)
        return move_text

    def set_start_end_time(self, timepoint):
        # 40*60*60 fromtimestamp接收的数太小就会出问题
        t = 144000
        # 记录显示时间 用于计算字幕运动速度 在某刻的位置 最终决定弹幕分布选择
        show_time = 15 #randint(10, 20)
        st = t + timepoint
        et = t + timepoint + show_time
        start_time = datetime.fromtimestamp(st).strftime("%H:%M:%S.%f")[1:][:-4]
        end_time = datetime.fromtimestamp(et).strftime("%H:%M:%S.%f")[1:][:-4]
        return start_time, end_time, show_time

    def set_random_font(self, line=""):
        font = self.font
        return font