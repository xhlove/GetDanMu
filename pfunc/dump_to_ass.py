#!/usr/bin/env python
# coding=utf-8
'''
# 作者: weimo
# 创建日期: 2020-01-04 19:17:44
# 上次编辑时间       : 2020-01-04 19:30:24
# 一个人的命运啊,当然要靠自我奋斗,但是...
'''

import os

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