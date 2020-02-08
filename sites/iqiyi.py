#!/usr/bin/env python3.7
# coding=utf-8
'''
# 作者: weimo
# 创建日期: 2020-01-04 19:14:41
# 上次编辑时间       : 2020-02-08 21:37:36
# 一个人的命运啊,当然要靠自我奋斗,但是...
'''

import json
import requests

from zlib import decompress
from xmltodict import parse

from basic.vars import iqiyiplayer
from pfunc.dump_to_ass import check_file, write_one_video_subtitles
from pfunc.request_info import get_vinfos, get_vinfos_by_url, get_vinfo_by_tvid


def get_danmu_by_tvid(name, duration, tvid):
    # http://cmts.iqiyi.com/bullet/41/00/10793494100_300_3.z
    if tvid.__class__ == int:
        tvid = str(tvid)
    api_url = "http://cmts.iqiyi.com/bullet/{}/{}/{}_{}_{}.z"
    timestamp = 300
    index = 0
    max_index = duration // timestamp + 1
    comments = []
    while index < max_index:
        url = api_url.format(tvid[-4:-2], tvid[-2:], tvid, timestamp, index + 1)
        # print(url)
        try:
            r = requests.get(url, headers=iqiyiplayer).content
        except Exception as e:
            print("error info -->", e)
            continue
        try:
            raw_xml = decompress(bytearray(r), 15+32).decode('utf-8')
        except Exception as e:
            index += 1
            continue
        try:
            entry = parse(raw_xml)["danmu"]["data"]["entry"]
        except Exception as e:
            index += 1
            continue
        # with open("raw_xml.json", "w", encoding="utf-8") as f:
        #     f.write(json.dumps(parse(raw_xml), ensure_ascii=False, indent=4))
        if entry.__class__ != list:
            entry = [entry]
        for comment in entry:
            if comment.get("list") is None:
                continue
            bulletInfo = comment["list"]["bulletInfo"]
            if bulletInfo.__class__ != list:
                bulletInfo = [bulletInfo]
            for info in bulletInfo:
                color = [info["color"]]
                comments.append([info["content"], color, int(comment["int"])])
        print("已下载{:.2f}%".format(index * timestamp * 100 / duration))
        index += 1
    comments = sorted(comments, key=lambda _: _[-1])
    return comments


def main(args):
    vinfos = []
    isall = False
    if args.series:
        isall = True
    if args.tvid:
        vi = get_vinfo_by_tvid(args.tvid, isall=isall)
        if vi:
            vinfos.append(vi)
    if args.aid:
        vi = get_vinfos(args.aid)
        if vi:
            vinfos += vi
    if args.tvid == "" and args.aid == "" and args.url == "":
        args.url = input("请输入iqiyi链接：\n")
    if args.url:
        vi = get_vinfos_by_url(args.url, isall=isall)
        if vi:
            vinfos += vi
    subtitles = {}
    for name, duration, tvid in vinfos:
        print(name, "开始下载...")
        flag, file_path = check_file(name, args)
        if flag is False:
            print("跳过{}".format(name))
            continue
        comments = get_danmu_by_tvid(name, duration, tvid)
        comments = write_one_video_subtitles(file_path, comments, args)
        subtitles.update({file_path:comments})
    return subtitles