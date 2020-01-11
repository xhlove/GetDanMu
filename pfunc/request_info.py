#!/usr/bin/env python3.7
# coding=utf-8
'''
# 作者: weimo
# 创建日期: 2020-01-04 19:14:43
# 上次编辑时间       : 2020-01-11 17:42:30
# 一个人的命运啊,当然要靠自我奋斗,但是...
'''
import re
import json
import requests

from time import localtime
from pfunc.cfunc import check_url_locale
from basic.vars import qqlive, iqiyiplayer, chrome

# 放一些仅通过某个id获取另一个/多个id的方法

#---------------------------------------------qq---------------------------------------------

def get_danmu_target_id_by_vid(vid: str):
    api_url = "http://bullet.video.qq.com/fcgi-bin/target/regist"
    params = {
        "otype":"json",
        "vid":vid
    }
    try:
        r = requests.get(api_url, params=params, headers=qqlive).content.decode("utf-8")
    except Exception as e:
        print("target_id requests error info -->", e)
        return None
    data = json.loads(r.lstrip("QZOutputJson=").rstrip(";"))
    target_id = None
    if data.get("targetid"):
        target_id = data["targetid"]
    return target_id

def get_all_vids_by_column_id():
    # https://s.video.qq.com/get_playsource?id=85603&plat=2&type=4&data_type=3&video_type=10&year=2019&month=&plname=qq&otype=json
    # 综艺类型的
    pass

def get_all_vids_by_cid(cid):
    api_url = "http://union.video.qq.com/fcgi-bin/data"
    params = {
        "tid":"431",
        "appid":"10001005",
        "appkey":"0d1a9ddd94de871b",
        "idlist":cid,
        "otype":"json"
    }
    r = requests.get(api_url, params=params, headers=qqlive).content.decode("utf-8")
    data = json.loads(r.lstrip("QZOutputJson=").rstrip(";"))
    try:
        nomal_ids = json.loads(data["results"][0]["fields"]["nomal_ids"])
    except Exception as e:
        print("load nomal_ids error info -->", e)
        return None
    # F 2是免费 7是会员 0是最新正片之前的预告 4是正片之后的预告
    vids = [item["V"] for item in nomal_ids if item["F"] in [2, 7]]
    return vids

#---------------------------------------------qq---------------------------------------------

#-------------------------------------------iqiyi--------------------------------------------

def get_vinfos(aid, locale="zh_cn"):
    api_url = "http://cache.video.iqiyi.com/avlist/{}/0/".format(aid)
    if locale != "zh_cn":
        api_url += "?locale=" + locale
    try:
        r = requests.get(api_url, headers=chrome, timeout=5).content.decode("utf-8")
    except Exception as e:
        print("get_vinfos requests error info -->", e)
        return None
    data = json.loads(r[len("var videoListC="):])
    try:
        vlist = data["data"]["vlist"]
    except Exception as e:
        print("get_vinfos load vlist error info -->", e)
        return None
    vinfos = [[v["shortTitle"] + "_" + str(v["timeLength"]), v["timeLength"], ["id"]] for v in vlist]
    return vinfos

def matchit(patterns, text):
    ret = None
    for pattern in patterns:
        match = re.match(pattern, text)
        if match:
            ret = match.group(1)
            break
    return ret

def duration_to_sec(duration):
    return sum(x * int(t) for x, t in zip([3600, 60, 1][2 - duration.count(":"):], duration.split(":")))

def get_year_range(aid, locale="zh_cn"):
    # 获取第一个和最新一个视频的年份，生成列表返回，遇到任何错误则返回当前年份
    year_start = year_end = localtime().tm_year
    api_url = "http://pcw-api.iqiyi.com/album/album/baseinfo/{}".format(aid)
    if locale != "zh_cn":
        api_url += "?locale=" + locale
    try:
        r = requests.get(api_url, headers=chrome, timeout=5).content.decode("utf-8")
    except Exception as e:
        print("error info -->", e)
        return list(range(year_start, year_end + 1))
    data = json.loads(r)["data"]
    if data.get("firstVideo"):
        year_start = int(data["firstVideo"]["period"][:4])
    if data.get("latestVideo"):
        year_end = int(data["latestVideo"]["period"][:4])
    return list(range(year_start, year_end + 1))

def get_vinfo_by_tvid(tvid, locale="zh_cn"):
    api_url = "https://pcw-api.iqiyi.com/video/video/baseinfo/{}".format(tvid)
    if locale != "zh_cn":
        api_url += "?locale=" + locale
    try:
        r = requests.get(api_url, headers=chrome, timeout=5).content.decode("utf-8")
    except Exception as e:
        print("error info -->", e)
        return
    data = json.loads(r)["data"]
    if data.__class__ != dict:
        return None
    name = data["name"]
    duration = data["durationSec"]
    return [name + "_" + str(duration), duration, tvid]

def get_vinfos_by_year(aid, years: list, cid=6, locale="zh_cn"):
    api_url = "https://pcw-api.iqiyi.com/album/source/svlistinfo?cid={}&sourceid={}&timelist={}".format(cid, aid, ",".join([str(_) for _ in years.copy()]))
    if locale != "zh_cn":
        api_url += "&locale=" + locale
    try:
        r = requests.get(api_url, headers=chrome, timeout=5).content.decode("utf-8")
    except Exception as e:
        print("get_vinfos_by_year error info -->", e)
        return None
    data = json.loads(r)["data"]
    vinfos = []
    for year in years:
        if year.__class__ != str:
            year = str(year)
        if data.get(year) is None:
            continue
        for ep in data[year]:
            sec = duration_to_sec(ep["duration"])
            vinfos.append([ep["shortTitle"] + "_" + str(sec), sec, ep["tvId"]])
    return vinfos

def get_vinfos_by_url(url):
    locale = check_url_locale(url)
    patterns = [".+?/w_(\w+?).html", ".+?/v_(\w+?).html", ".+?/a_(\w+?).html", ".+?/lib/m_(\w+?).html"]
    isw, isep, isas, isms = [re.match(pattern, url) for pattern in patterns]
    if isw is None and isep is None and isas is None and isms is None:
        return None
    try:
        r = requests.get(url, headers=chrome, timeout=5).content.decode("utf-8")
    except Exception as e:
        print("get_vinfos_by_url error info -->", e)
        return None
    cid_patterns = ["[\s\S]+?\.cid.+?(\d+)", "[\s\S]+?cid: \"(\d+)\"", "[\s\S]+?channelID.+?\"(\d+)\""]
    cid = matchit(cid_patterns, r)
    aid_patterns = ["[\s\S]+?aid:'(\d+)'", "[\s\S]+?albumid=\"(\d+)\"", "[\s\S]+?movlibalbumaid=\"(\d+)\"", "[\s\S]+?data-score-tvid=\"(\d+)\""]
    aid = matchit(aid_patterns, r)
    tvid_patterns = ["[\s\S]+?\"tvid\":\"(\d+)\"", "[\s\S]+?\['tvid'\].+?\"(\d+)\""]
    tvid = matchit(tvid_patterns, r)
    if cid is None:
        cid = ""
    elif cid == "6" and isas or isms:#对于综艺合集需要获取年份
        # year_patterns = ["[\s\S]+?datePublished.+?(\d\d\d\d)-\d\d-\d\d", "[\s\S]+?data-year=\"(\d+)\""]
        # year = matchit(year_patterns, r)
        # if year is None:
        #     years = [localtime().tm_year]
        # else:
        #     years = [year]
        years = get_year_range(aid, locale=locale)
    else:
        pass#暂时没有其他的情况计划特别处理

    if isep or isw:
        if tvid is None:
            return
        return get_vinfo_by_tvid(tvid, locale=locale)

    if isas or isms:
        if aid is None:
            return
        if cid == "6":
            return get_vinfos_by_year(aid, years, locale=locale)
        else:
            return get_vinfos(aid, locale=locale)

#-------------------------------------------iqiyi--------------------------------------------

#-------------------------------------------youku--------------------------------------------

def get_vinfos_by_url_youku(url, isall=False):
    vid_patterns = ["[\s\S]+?youku.com/video/id_(/+?)\.html", "[\s\S]+?youku.com/v_show/id_(.+?)\.html"]
    video_id = matchit(vid_patterns, url)
    show_id_patterns = ["[\s\S]+?youku.com/v_nextstage/id_(/+?)\.html", "[\s\S]+?youku.com/show/id_z(.+?)\.html", "[\s\S]+?youku.com/show_page/id_z(.+?)\.html", "[\s\S]+?youku.com/alipay_video/id_(.+?)\.html"]
    show_id = matchit(show_id_patterns, url)
    if video_id is None and show_id is None:
        return None
    if video_id:
        return get_vinfos_by_video_id(video_id, isall=isall)
    if show_id.__len__() == 20 and show_id == show_id.lower():
        return get_vinfos_by_show_id(show_id)
    else:
        return get_vinfos_by_video_id(show_id, isall=isall)

def get_vinfos_by_video_id(video_id, isall=False):
    api_url = "https://openapi.youku.com/v2/videos/show.json?client_id=53e6cc67237fc59a&package=com.huawei.hwvplayer.youku&ext=show&video_id={}".format(video_id)
    try:
        r = requests.get(api_url, headers=chrome, timeout=5).content.decode("utf-8")
    except Exception as e:
        print("get_vinfos_by_video_id error info -->", e)
        return None
    data = json.loads(r)
    if isall:
        show_id = data["show"]["id"]
        return get_vinfos_by_show_id(show_id)
    duration = 0
    if data.get("duration"):
        duration = int(float(data["duration"]))
    if data.get("title"):
        name = data["title"] + "_" + str(duration)
    else:
        name = "优酷未知" + "_" + str(duration)
    vinfo = [name, duration, video_id]
    return [vinfo]

def get_vinfos_by_show_id(show_id):
    api_url = "https://openapi.youku.com/v2/shows/videos.json?show_videotype=正片&count=100&client_id=53e6cc67237fc59a&page=1&show_id={}&package=com.huawei.hwvplayer.youku".format(show_id)
    try:
        r = requests.get(api_url, headers=chrome, timeout=5).content.decode("utf-8")
    except Exception as e:
        print("get_vinfos_by_show_id error info -->", e)
        return None
    data = json.loads(r)["videos"]
    if data.__len__() == 0:
        return None
    vinfos = []
    for video in data:
        duration = 0
        if video.get("duration"):
            duration = int(float(video["duration"]))
        if video.get("title"):
            name = video["title"] + "_" + str(duration)
        else:
            name = "优酷未知_{}".format(video["id"]) + "_" + str(duration)
        vinfos.append([name, duration, video["id"]])
    return vinfos
#-------------------------------------------youku--------------------------------------------