#!/usr/bin/env python3.7
# coding=utf-8
'''
# 作者: weimo
# 创建日期: 2020-01-05 14:52:21
# 上次编辑时间       : 2020-01-11 17:53:14
# 一个人的命运啊,当然要靠自我奋斗,但是...
'''
import re
import time
import json
import base64
import requests

from basic.vars import chrome
from pfunc.dump_to_ass import check_file, write_one_video_subtitles
from pfunc.cfunc import yk_msg_sign, yk_t_sign
from pfunc.request_info import get_vinfos_by_show_id, get_vinfos_by_video_id, get_vinfos_by_url_youku

def get_tk_enc():
    """
    获取优酷的_m_h5_tk和_m_h5_tk_enc
    """
    api_url = "https://acs.youku.com/h5/mtop.com.youku.aplatform.weakget/1.0/?jsv=2.5.1&appKey=24679788"
    try:
        r = requests.get(api_url, headers=chrome, timeout=5)
    except Exception as e:
        return
    tk_enc = dict(r.cookies)
    if tk_enc.get("_m_h5_tk_enc") and tk_enc.get("_m_h5_tk"):
        return tk_enc
    return

def get_cna():
    api_url = "https://log.mmstat.com/eg.js"
    try:
        r = requests.get(api_url, headers=chrome, timeout=5)
    except Exception as e:
        return
    cookies = dict(r.cookies)
    if cookies.get("cna"):
        return cookies["cna"]
    return

def get_danmu_by_mat(vid, cna, mat: int, comments: list):
    api_url = "https://acs.youku.com/h5/mopen.youku.danmu.list/1.0/"
    tm = str(int(time.time() * 1000))
    msg = {
        "ctime": tm,
        "ctype": 10004,
        "cver": "v1.0",
        "guid": cna,
        "mat": mat,
        "mcount": 1,
        "pid": 0,
        "sver": "3.1.0",
        "type": 1,
        "vid": vid}
    msg_b64encode = base64.b64encode(json.dumps(msg, separators=(',', ':')).encode("utf-8")).decode("utf-8")
    msg.update({"msg":msg_b64encode})
    msg.update({"sign":yk_msg_sign(msg_b64encode)})
    # 测试发现只要有Cookie的_m_h5_tk和_m_h5_tk_enc就行
    tk_enc = get_tk_enc()
    if tk_enc is None:
        return
    headers = {
        "Content-Type":"application/x-www-form-urlencoded",
        "Cookie":";".join([k + "=" + v for k, v in tk_enc.items()]),
        "Referer": "https://v.youku.com"
    }
    headers.update(chrome)
    t = str(int(time.time() * 1000))
    data = json.dumps(msg, separators=(',', ':'))
    params = {
        "jsv":"2.5.6",
        "appKey":"24679788",
        "t":t,
        "sign":yk_t_sign(tk_enc["_m_h5_tk"][:32], t, "24679788", data),
        "api":"mopen.youku.danmu.list",
        "v":"1.0",
        "type":"originaljson",
        "dataType":"jsonp",
        "timeout":"20000",
        "jsonpIncPrefix":"utility"
    }
    try:
        r = requests.post(api_url, params=params, data={"data":data}, headers=headers, timeout=5).content.decode("utf-8")
    except Exception as e:
        print("youku danmu request failed.", e)
        return "once again"
    result = json.loads(json.loads(r)["data"]["result"])["data"]["result"]
    for item in result:
        comment = item["content"]
        c_int = json.loads(item["propertis"])["color"]
        if c_int.__class__ == str:
            c_int = int(c_int)
        color = hex(c_int)[2:].zfill(6)
        timepoint = item["playat"] / 1000
        comments.append([comment, [color], timepoint])
    return comments

def main(args):
    cna = get_cna()
    if cna is None:
        # 放前面 免得做无用功
        return
    isall = False
    if args.series:
        isall = True
    vinfos = []
    if args.url:
        vi = get_vinfos_by_url_youku(args.url, isall=isall)
        if vi:
            vinfos += vi
    if args.vid:
        vi = get_vinfos_by_video_id(args.vid, isall=isall)
        if vi:
            vinfos += vi
    subtitles = {}
    for name, duration, video_id in vinfos:
        print(name, "开始下载...")
        flag, file_path = check_file(name, skip=args.y)
        if flag is False:
            print("跳过{}".format(name))
            continue
        max_mat = duration // 60 + 1
        comments = []
        for mat in range(max_mat):
            result = get_danmu_by_mat(video_id, cna, mat + 1, comments)
            if result is None:
                continue
            elif result == "once again":
                # 可能改成while好点
                result = get_danmu_by_mat(video_id, cna, mat + 1, comments)
                if result is None:
                    continue
            comments = result
            print("已下载{}/{}".format(mat + 1, max_mat))
        comments = write_one_video_subtitles(file_path, comments, args)
        subtitles.update({file_path:comments})
    return subtitles