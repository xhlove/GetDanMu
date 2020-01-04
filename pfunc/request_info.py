#!/usr/bin/env python
# coding=utf-8
'''
# 作者: weimo
# 创建日期: 2020-01-04 13:15:25
# 上次编辑时间       : 2020-01-04 17:47:16
# 一个人的命运啊,当然要靠自我奋斗,但是...
'''

import re
import json
import requests

from basic.vars import qqlive, iqiyiplayer

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
        print("error info -->", e)
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
        print("error info -->", e)
        return None
    # F 2是免费 7是会员 0是最新正片之前的预告 4是正片之后的预告
    vids = [item["V"] for item in nomal_ids if item["F"] in [2, 7]]
    return vids

#---------------------------------------------qq---------------------------------------------

#-------------------------------------------iqiyi--------------------------------------------

def get_vinfos(aid):
    api_url = "http://cache.video.iqiyi.com/avlist/{}/0/".format(aid)
    try:
        r = requests.get(api_url, headers=iqiyiplayer).content.decode("utf-8")
    except Exception as e:
        print("error info -->", e)
        return None
    data = json.loads(r[len("var videoListC="):])
    try:
        vlist = data["data"]["vlist"]
    except Exception as e:
        print("error info -->", e)
        return None
    vinfos = [[v["shortTitle"] + "_" + str(v["timeLength"]), v["timeLength"], ["id"]] for v in vlist]
    return vinfos

def get_vinfos_by_url(url):
    pass

#-------------------------------------------iqiyi--------------------------------------------