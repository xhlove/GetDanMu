#!/usr/bin/env python
# coding=utf-8
'''
# 作者: weimo
# 创建日期: 2019-12-18 09:48:36
# 上次编辑时间       : 2020-01-04 17:54:46
# 一个人的命运啊,当然要靠自我奋斗,但是...
'''

import json
import requests

from zlib import decompress
from xmltodict import parse

from basic.vars import iqiyiplayer
from basic.ass import check_content
from pfunc.dump_to_ass import check_file
from pfunc.request_info import get_vinfos


def get_vinfo_by_tvid(tvid):
    api_url = "https://pcw-api.iqiyi.com/video/video/baseinfo/{}".format(tvid)
    try:
        r = requests.get(api_url, headers=iqiyiplayer).content.decode("utf-8")
    except Exception as e:
        print("error info -->", e)
        return
    data = json.loads(r)["data"]
    if data.__class__ != dict:
        return None
    name = data["name"]
    duration = data["durationSec"]
    return [name + "_" + str(duration), duration, tvid]

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
        raw_xml = decompress(bytearray(r), 15+32).decode('utf-8')
        try:
            entry = parse(raw_xml)["danmu"]["data"]["entry"]
        except Exception as e:
            index += 1
            continue
        # with open("raw_xml.json", "w", encoding="utf-8") as f:
        #     f.write(json.dumps(parse(raw_xml), ensure_ascii=False, indent=4))
        contents = []
        if entry.__class__ != list:
            entry = [entry]
        for comment in entry:
            bulletInfo = comment["list"]["bulletInfo"]
            if bulletInfo.__class__ != list:
                bulletInfo = [bulletInfo]
            for info in bulletInfo:
                content = check_content(info["content"], contents)
                if content is None:
                    continue
                else:
                    contents.append(content)
                color = [info["color"]]
                comments.append([content, color, int(comment["int"])])
        print("已下载{:.2f}%".format(index * timestamp * 100 / duration))
        index += 1
    comments = sorted(comments, key=lambda _: _[-1])
    return comments


def main(args):
    vinfos = []
    if args.tvid:
        vi = get_vinfo_by_tvid(args.tvid)
        if vi:
            vinfos.append(vi)
    if args.aid:
        vi = get_vinfos(args.aid)
        if vi:
            vinfos += vi
    # if args.url:
    #     vi = get_vinfos_by_url(args.url)
    #     if vi:
    #         vinfos += vi
    subtitles = {}
    for name, duration, tvid in vinfos:
        print(name, "开始下载...")
        flag, file_path = check_file(name, skip=args.y)
        if flag is False:
            print("跳过{}".format(name))
            return
        comments = get_danmu_by_tvid(name, duration, tvid)
        subtitles.update({file_path:comments})
    return subtitles