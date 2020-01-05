#!/usr/bin/env python3.7
# coding=utf-8
'''
# 作者: weimo
# 创建日期: 2020-01-04 19:17:44
# 上次编辑时间: 2020-01-05 14:45:03
# 一个人的命运啊,当然要靠自我奋斗,但是...
'''
import os

from basic.ass import get_ass_head, check_font
from methods.assbase import ASS
from methods.sameheight import SameHeight

def write_one_video_subtitles(file_path, comments, args):
    # 对于合集则每次都都得检查一次 也可以放在上一级 放在这里 考虑后面可能特殊指定字体的情况
    font_path, font_style_name = check_font(args.font)
    ass_head = get_ass_head(font_style_name, args.font_size)
    get_xy_obj = SameHeight("那就写这一句作为初始化测试吧！", font_path=font_path, font_size=args.font_size)
    subtitle = ASS(file_path, get_xy_obj, font=font_style_name)
    for comment in comments:
        subtitle.create_new_line(comment)
    write_lines_to_file(ass_head, subtitle.lines, file_path)

def write_lines_to_file(ass_head, lines, file_path):
    with open(file_path, "a+", encoding="utf-8") as f:
        f.write(ass_head + "\n")
        for line in lines:
            f.write(line + "\n")

def check_file(name, skip=False, fpath=os.getcwd()):
    flag = True
    file_path = os.path.join(fpath, name + ".ass")
    if os.path.isfile(file_path):
        if skip:
            os.remove(file_path)
        else:
            isremove = input("{}已存在，是否覆盖？(y/n)：".format(file_path))
            if isremove.strip() == "y":
                os.remove(file_path)
            else:
                flag = False
                return flag, file_path
    with open(file_path, "wb") as f:
        pass
    return flag, file_path