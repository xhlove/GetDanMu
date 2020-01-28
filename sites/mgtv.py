#!/usr/bin/env python3.7
# coding=utf-8
'''
# 作者: weimo
# 创建日期: 2020-01-28 15:55:22
# 上次编辑时间       : 2020-01-28 19:57:57
# 一个人的命运啊,当然要靠自我奋斗,但是...
'''
import re
import json
import time
import base64
import requests
from uuid import uuid4
from collections import OrderedDict

from basic.vars import chrome
from pfunc.request_info import duration_to_sec
from pfunc.dump_to_ass import check_file, write_one_video_subtitles

pno_params = {
    "pad":"1121",
    "ipad":"1030"
}
type_params = {
    "h5flash":"h5flash",
    "padh5":"padh5",
    "pch5":"pch5"
}

def get_danmu_by_vid(vid: str, cid: str, duration: int):
    api_url = "https://galaxy.bz.mgtv.com/rdbarrage"
    params = OrderedDict({
        "version": "2.0.0",
        "vid": vid,
        "abroad": "0",
        "pid": "",
        "os": "",
        "uuid": "",
        "deviceid": "",
        "cid": cid,
        "ticket": "",
        "time": "0",
        "mac": "",
        "platform": "0",
        "callback": ""
    })
    comments = []
    index = 0
    max_index = duration // 60 + 1
    while index < max_index:
        params["time"] = str(index * 60 * 1000)
        try:
            r = requests.get(api_url, params=params, headers=chrome, timeout=3).content.decode("utf-8")
        except Exception as e:
            continue
        items = json.loads(r)["data"]["items"]
        index += 1
        if items is None:
            continue
        for item in items:
            comments.append([item["content"], ["ffffff"], int(item["time"] / 1000)])
        print("已下载{:.2f}%".format(index / max_index * 100))
    return comments

def get_tk2(did):
    pno = pno_params["ipad"]
    ts = str(int(time.time()))
    text = f"did={did}|pno={pno}|ver=0.3.0301|clit={ts}"
    tk2 = base64.b64encode(text.encode("utf-8")).decode("utf-8").replace("+", "_").replace("/", "~").replace("=", "-")
    return tk2[::-1]

def get_vinfos_by_cid_or_vid(xid: str, flag="vid"):
    api_url = "https://pcweb.api.mgtv.com/episode/list"
    params = {
        "video_id": xid,
        "page": "0",
        "size": "25",
        "cxid": "",
        "version": "5.5.35",
        "callback": "",
        "_support": "10000000",
        "_": str(int(time.time() * 1000))
    }
    if flag == "cid":
        _ = params.pop("video_id")
        params["collection_id"] = xid
    page = 1
    vinfos = []
    while True:
        params["page"] = page
        try:
            r = requests.get(api_url, params=params, headers=chrome, timeout=3).content.decode("utf-8")
        except Exception as e:
            continue
        data = json.loads(r)["data"]
        for ep in data["list"]:
            if re.match("\d\d\d\d-\d\d-\d\d", ep["t4"]):
                # 综艺的加上日期
                name = "{t4}_{t3}_{t2}".format(**ep).replace(" ", "")
            else:
                name = "{t3}_{t2}".format(**ep).replace(" ", "")
            duration = duration_to_sec(ep["time"])
            vinfos.append([name, duration, ep["video_id"], ep["clip_id"]])
        if page < data["count"] // 25 + 1:
            page += 1
        else:
            break
    return vinfos

def get_vinfo_by_vid(vid: str):
    api_url = "https://pcweb.api.mgtv.com/player/video"
    type_ = type_params["pch5"]
    did = uuid4().__str__()
    suuid = uuid4().__str__()
    params = OrderedDict({
        "did": did,
        "suuid": suuid,
        "cxid": "",
        "tk2": get_tk2(did),
        "video_id": vid,
        "type": type_,
        "_support": "10000000",
        "auth_mode": "1",
        "callback": ""
    })
    try:
        r = requests.get(api_url, params=params, headers=chrome, timeout=3).content.decode("utf-8")
    except Exception as e:
        return
    info = json.loads(r)["data"]["info"]
    name = "{title}_{series}_{desc}".format(**info).replace(" ", "")
    duration = int(info["duration"])
    cid = info["collection_id"]
    return [name, duration, vid, cid]

def get_vinfos_by_url(url: str, isall: bool):
    vinfos = []
    # url = https://www.mgtv.com/b/323323/4458375.html
    ids = re.match("[\s\S]+?mgtv.com/b/(\d+)/(\d+)\.html", url)
    # url = "https://www.mgtv.com/h/333999.html?fpa=se"
    cid_v1 = re.match("[\s\S]+?mgtv.com/h/(\d+)\.html", url)
    # url = "https://m.mgtv.com/h/333999/0.html"
    cid_v2 = re.match("[\s\S]+?mgtv.com/h/(\d+)/\d\.html", url)
    if ids is None and cid_v1 is None and cid_v2 is None:
        return
    if ids and ids.groups().__len__() == 2:
        cid, vid = ids.groups()
        if isall:
            vi = get_vinfos_by_cid_or_vid(vid)
            if vi:
                vinfos += vi
        else:
            vinfo = get_vinfo_by_vid(vid)
            if vinfo is None:
                return
            vinfos.append(vinfo)
    print("ccc", cid_v1)
    if cid_v1 or cid_v2:
        if cid_v2 is None:
            cid = cid_v1.group(1)
        else:
            cid = cid_v2.group(1)
        vi = get_vinfos_by_cid_or_vid(cid, flag="cid")
        if vi:
            vinfos += vi
    return vinfos

def main(args):
    vinfos = []
    isall = False
    if args.series:
        isall = True
    if args.url:
        vi = get_vinfos_by_url(args.url, isall)
        if vi:
            vinfos += vi
    if args.vid:
        if isall:
            vi = get_vinfos_by_cid_or_vid(args.vid)
            if vi:
                vinfos += vi
        else:
            vi = get_vinfo_by_vid(args.vid)
            if vi:
                vinfos.append(vi)
    if args.cid:
        vi = get_vinfos_by_cid_or_vid(args.cid)
        if vi:
            vinfos += vi
    subtitles = {}
    for name, duration, vid, cid in vinfos:
        print(name, "开始下载...")
        flag, file_path = check_file(name, args)
        if flag is False:
            print("跳过{}".format(name))
            continue
        comments = get_danmu_by_vid(vid, cid, duration)
        write_one_video_subtitles(file_path, comments, args)
        subtitles.update({file_path:comments})
        print(name, "下载完成！")
    return subtitles

if __name__ == "__main__":
    args = object()
    args.url = "https://www.mgtv.com/h/333999.html?fpa=se"
    main(args)