#!/usr/bin/env python3.7
# coding=utf-8
'''
# 作者: weimo
# 创建日期: 2020-01-04 19:14:39
# 上次编辑时间       : 2020-02-07 19:10:02
# 一个人的命运啊,当然要靠自我奋斗,但是...
'''

import sys

from argparse import ArgumentParser

from sites.qq import main as qq
from sites.iqiyi import main as iqiyi
from sites.youku import main as youku
from sites.sohu import main as sohu
from sites.mgtv import main as mgtv
from pfunc.cfunc import check_url_site

from basic.vars import ALLOW_SITES

# -------------------------------------------
# 基本流程
# 1. 根据传入参数确定网站，否则请求输入有关参数或链接。并初始化字幕的基本信息。
# 2. 解析链接得到相关视频/弹幕的参数，以及时长等
# 3. 根据网站对应接口获取全部弹幕
# 4. 转换弹幕
# 5. 写入字幕文件
# -------------------------------------------


def main():
    parser = ArgumentParser(description="视频网站弹幕转换/下载工具，项目地址https://github.com/xhlove/GetDanMu，任何问题请联系vvtoolbox.dev@gmail.com")
    parser.add_argument("-f", "--font", default="微软雅黑", help="指定输出字幕字体")
    parser.add_argument("-fs", "--font-size", default=28, help="指定输出字幕字体大小")
    parser.add_argument("-s", "--site", default="", help=f"使用非url方式下载需指定网站 支持的网站 -> {' '.join(ALLOW_SITES)}")
    parser.add_argument("-r", "--range", default="0,720", help="指定弹幕的纵向范围 默认0到720 请用逗号隔开")
    parser.add_argument("-cid", "--cid", default="", help="下载cid对应视频的弹幕（腾讯 芒果视频合集）")
    parser.add_argument("-vid", "--vid", default="", help="下载vid对应视频的弹幕，支持同时多个vid，需要用逗号隔开")
    parser.add_argument("-aid", "--aid", default="", help="下载aid对应视频的弹幕（爱奇艺合集）")
    parser.add_argument("-tvid", "--tvid", default="", help="下载tvid对应视频的弹幕，支持同时多个tvid，需要用逗号隔开")
    parser.add_argument("-series", "--series", action="store_true", help="尝试通过单集得到合集的全部弹幕")
    parser.add_argument("-u", "--url", default="", help="下载视频链接所指向视频的弹幕")
    parser.add_argument("-y", "--y", action="store_true", help="默认覆盖原有弹幕而不提示")
    args = parser.parse_args()
    # print(args.__dict__)
    init_args = sys.argv
    imode = "command_line"
    if init_args.__len__() == 1:
        # 双击运行或命令执行exe文件时 传入参数只有exe的路径 
        # 命令行下执行会传入exe的相对路径（在exe所在路径执行时） 传入完整路径（非exe所在路径下执行）
        # 双击运行exe传入完整路径
        imode = "non_command_line"
    if imode == "non_command_line":
        content = input("请输入链接：\n")
        check_tip = check_url_site(content)
        if check_tip is None:
            sys.exit("不支持的网站")
        args.url = content
        args.site = check_tip
    # 要么有url 要么有site和相关参数的组合
    if args.url != "":
        args.site = check_url_site(args.url)
    elif args.site == "":
        sys.exit("请传入链接或指定网站+视频相关的参数")
    if args.site == "qq":
        subtitles = qq(args)
    if args.site == "iqiyi":
        subtitles = iqiyi(args)
    if args.site == "youku":
        subtitles = youku(args)
    if args.site == "sohu":
        subtitles = sohu(args)
    if args.site == "mgtv":
        subtitles = mgtv(args)

if __name__ == "__main__":
    # 打包 --> pyinstaller GetDanMu.spec
    main()