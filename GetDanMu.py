#!/usr/bin/env python
# coding=utf-8
'''
# 作者: weimo
# 创建日期: 2020-01-04 12:59:11
# 上次编辑时间       : 2020-01-04 17:41:34
# 一个人的命运啊,当然要靠自我奋斗,但是...
'''

import sys

from argparse import ArgumentParser

from sites.qq import main as qq
from sites.iqiyi import main as iqiyi
from basic.ass import get_ass_head, check_font
from pfunc.dump_to_ass import write_lines_to_file
from methods.assbase import ASS
from methods.sameheight import SameHeight

# -------------------------------------------
# 基本流程
# 1. 根据传入参数确定网站，否则请求输入有关参数或链接。并初始化字幕的基本信息。
# 2. 解析链接得到相关视频/弹幕的参数，以及时长等
# 3. 根据网站对应接口获取全部弹幕
# 4. 转换弹幕
# 5. 写入字幕文件
# -------------------------------------------


def main():
    parser = ArgumentParser(description="视频网站弹幕转换/下载工具，任何问题请联系vvtoolbox.dev@gmail.com")
    parser.add_argument("-f", "--font", default="微软雅黑", help="指定输出字幕字体")
    parser.add_argument("-fs", "--font-size", default=28, help="指定输出字幕字体大小")
    parser.add_argument("-s", "--site", default="qq", help="指定网站")
    parser.add_argument("-cid", "--cid", default="", help="下载cid对应视频的弹幕（腾讯视频合集）")
    parser.add_argument("-vid", "--vid", default="", help="下载vid对应视频的弹幕，支持同时多个vid，需要用逗号隔开")
    parser.add_argument("-aid", "--aid", default="", help="下载aid对应视频的弹幕（爱奇艺合集）")
    parser.add_argument("-tvid", "--tvid", default="", help="下载tvid对应视频的弹幕，支持同时多个tvid，需要用逗号隔开")
    parser.add_argument("-u", "--url", default="", help="下载视频链接所指向视频的弹幕")
    parser.add_argument("-y", "--y", action="store_true", help="覆盖原有弹幕而不提示")
    args = parser.parse_args()
    print(args.__dict__)
    font_path, font_style_name = check_font(args.font)
    ass_head = get_ass_head(font_style_name, args.font_size)
    if args.site == "qq":
        subtitles = qq(args)
    if args.site == "iqiyi":
        subtitles = iqiyi(args)

    for file_path, comments in subtitles.items():
        get_xy_obj = SameHeight("那就写这一句作为初始化测试吧！", font_path=font_path, font_size=args.font_size)
        subtitle = ASS(file_path, get_xy_obj, font=font_style_name)
        for comment in comments:
            subtitle.create_new_line(comment)
        write_lines_to_file(ass_head, subtitle.lines, file_path)

if __name__ == "__main__":
    # 打包 --> pyinstaller -F .\qq.py -c -n GetDanMu_qq_1.1
    main()
    # subtitle = ASS()