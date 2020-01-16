#!/usr/bin/env python3.7
# coding=utf-8
'''
# 作者: weimo
# 创建日期: 2020-01-16 17:45:35
# 上次编辑时间       : 2020-01-16 20:09:22
# 一个人的命运啊,当然要靠自我奋斗,但是...
'''
import json
import requests

from basic.vars import chrome
from pfunc.request_info import matchit
from pfunc.dump_to_ass import check_file, write_one_video_subtitles

def try_decode(content):
    flag = False
    methods = ["gbk", "utf-8"]
    for method in methods:
        try:
            content_decode = content.decode(method)
        except Exception as e:
            print("try {} decode method failed.".format(method))
            continue
        flag = True
        break
    if flag is True:
        return content_decode
    else:
        return None

def get_vinfos_by_url(url: str):
    ep_url = matchit(["[\s\S]+?tv.sohu.com/v/(.+?)\.html", "[\s\S]+?tv.sohu.com/(.+?)/(.+?)\.html"], url)
    aid_url = matchit(["[\s\S]+?tv.sohu.com/album/.(\d+)\.shtml"], url)
    vid_url = matchit(["[\s\S]+?tv.sohu.com/v(\d+)\.shtml"], url)
    if ep_url:
        try:
            r = requests.get(url, headers=chrome, timeout=3).content
        except Exception as e:
            print(e)
            print("get sohu (url -> {}) ep url failed.".format(url))
            return
        r_decode = try_decode(r)
        if r_decode is None:
            print("ep response use decode failed(url -> {}).".format(url))
            return None
        vid = matchit(["[\s\S]+?var vid.+?(\d+)"], r_decode)
        if vid:
            vinfo = get_vinfo_by_vid(vid)
            if vinfo is None:
                return
            else:
                return [vinfo]
        else:
            print("match sohu vid (url -> {}) failed.".format(url))
            return None
    if aid_url:
        return get_vinfos(aid_url)
    if vid_url:
        vinfo = get_vinfo_by_vid(vid_url)
        if vinfo is None:
            return
        else:
            return [vinfo]
    if ep_url is None and aid_url is None and vid_url is None:
        # 可能是合集页面
        try:
            r = requests.get(url, headers=chrome, timeout=3).content
        except Exception as e:
            print("get sohu (url -> {}) album url failed.".format(url))
            return
        r_decode = try_decode(r)
        if r_decode is None:
            print("album response decode failed(url -> {}).".format(url))
            return None
        aid = matchit(["[\s\S]+?var playlistId.+?(\d+)"], r_decode)
        if aid:
            return get_vinfos(aid)
    return


def get_vinfos(aid: str):
    api_url = "https://pl.hd.sohu.com/videolist"
    params = {
        "callback": "",
        "playlistid": aid,
        "o_playlistId": "",
        "pianhua": "0",
        "pagenum": "1",
        "pagesize": "999",
        "order": "0", # 0 从小到大
        "cnt": "1",
        "pageRule": "2",
        "withPgcVideo": "0",
        "ssl": "0",
        "preVideoRule": "3",
        "_": "" # 1579167883430
    }
    try:
        r = requests.get(api_url, params=params, headers=chrome, timeout=3).content.decode("gbk")
    except Exception as e:
        print("get sohu (vid -> {}) videolist failed.".format(vid))
        return None
    data = json.loads(r)
    if data.get("videos"):
        videos = data["videos"]
    else:
        print("videolist has no videos (aid -> {}).".format(aid))
        return None
    vinfos = [[video["name"], int(float(video["playLength"])), video["vid"], aid] for video in videos]
    return vinfos


def get_vinfo_by_vid(vid: str):
    api_url = "https://hot.vrs.sohu.com/vrs_flash.action"
    params = {
        "vid": vid,
        "ver": "31",
        "ssl": "1",
        "pflag": "pch5"
    }
    try:
        r = requests.get(api_url, params=params, headers=chrome, timeout=3).content.decode("utf-8")
    except Exception as e:
        print("get sohu (vid -> {}) vinfo failed.".format(vid))
        return None
    data = json.loads(r)
    if data.get("status") == 1:
        aid = ""
        if data.get("pid"):
            aid = str(data["pid"])
        if data.get("data"):
            data = data["data"]
        else:
            print("vid -> {} vinfo request return no data.".format(vid))
            return
    else:
        print("vid -> {} vinfo request return error.".format(vid))
        return
    return [data["tvName"], int(float(data["totalDuration"])), vid, aid]

def get_danmu_all_by_vid(vid: str, aid: str, duration: int):
    api_url = "https://api.danmu.tv.sohu.com/dmh5/dmListAll"
    params = {
        "act": "dmlist_v2",
        "dct": "1",
        "request_from": "h5_js",
        "vid": vid,
        "page": "1",
        "pct": "2",
        "from": "PlayerType.SOHU_VRS",
        "o": "4",
        "aid": aid,
        "time_begin": "0",
        "time_end": str(duration)
    }
    try:
        r = requests.get(api_url, params=params, headers=chrome, timeout=3).content.decode("utf-8")
    except Exception as e:
        print("get sohu (vid -> {}) danmu failed.".format(vid))
        return None
    data = json.loads(r)["info"]["comments"]
    comments = []
    for comment in data:
        comments.append([comment["c"], "ffffff", comment["v"]])
    comments = sorted(comments, key=lambda _: _[-1])
    return comments

def main(args):
    vinfos = []
    if args.vid:
        vi = get_vinfo_by_vid(args.vid)
        if vi:
            vinfos.append(vi)
    if args.aid:
        vi = get_vinfos(args.aid)
        if vi:
            vinfos += vi
    if args.vid == "" and args.aid == "" and args.url == "":
        args.url = input("请输入sohu链接：\n")
    if args.url:
        vi = get_vinfos_by_url(args.url)
        if vi:
            vinfos += vi
    subtitles = {}
    for name, duration, vid, aid in vinfos:
        print(name, "开始下载...")
        flag, file_path = check_file(name, args)
        if flag is False:
            print("跳过{}".format(name))
            continue
        comments = get_danmu_all_by_vid(vid, aid, duration)
        if comments is None:
            print(name, "弹幕获取失败了，记得重试~(@^_^@)~")
            continue
        comments = write_one_video_subtitles(file_path, comments, args)
        subtitles.update({file_path:comments})
        print(name, "下载完成！")
    return subtitles