#!/usr/bin/env python3.7
# coding=utf-8
'''
# 作者: weimo
# 创建日期: 2020-01-04 19:14:37
# 上次编辑时间: 2020-01-05 14:47:36
# 一个人的命运啊,当然要靠自我奋斗,但是...
'''

import os
import sys
import json
import requests

from basic.vars import qqlive
from basic.ass import check_content
from pfunc.dump_to_ass import check_file, write_one_video_subtitles
from pfunc.request_info import get_all_vids_by_cid as get_vids
from pfunc.request_info import get_danmu_target_id_by_vid as get_target_id


def get_video_info_by_vid(vids: list):
    idlist = ",".join(vids)
    api_url = "http://union.video.qq.com/fcgi-bin/data"
    params = {
        "tid":"98",
        "appid":"10001005",
        "appkey":"0d1a9ddd94de871b",
        "idlist":f"{idlist}",
        "otype":"json"
    }
    try:
        r = requests.get(api_url, params=params, headers=qqlive).content.decode("utf-8")
    except Exception as e:
        print("error info -->", e)
        return
    data = json.loads(r.lstrip("QZOutputJson=").rstrip(";"))
    if not data.get("results"):
        return
    subkey = ["title", "episode", "langue", "duration"]
    vinfos = []
    for index, item in enumerate(data["results"]):
        vid = [vids[index]]
        values = [str(item["fields"][key]) for key in subkey if item["fields"].get(key) is not None]
        name = "_".join(values)
        if item["fields"].get("duration"):
            duration = int(item["fields"]["duration"])
        else:
            duration = 0
        # target_id = item["fields"]["targetid"] # 这个target_id一般不是弹幕用的
        target_id = get_target_id(vid)
        if target_id is None:
            continue
        vinfos.append([vid, name, duration, target_id])
    # print(vinfos)
    return vinfos

def get_danmu_by_target_id(vid: str, duration: int, target_id, font="微软雅黑", font_size=25):
    # timestamp间隔30s 默认从15开始
    api_url = "https://mfm.video.qq.com/danmu"
    params = {
        "otype":"json",
        "target_id":"{}&vid={}".format(target_id, vid),
        "session_key":"0,0,0",
        "timestamp":15
    }
    # subtitle = ASS(file_path, font=font, font_size=font_size)
    comments = []
    while params["timestamp"] < duration:
        try:
            r = requests.get(api_url, params=params, headers=qqlive).content.decode("utf-8")
        except Exception as e:
            print("error info -->", e)
            continue
        try:
            danmu = json.loads(r)
        except Exception as e:
            danmu = json.loads(r, strict=False)
        if danmu.get("count") is None:
            # timestamp不变 再试一次
            continue
        danmu_count = danmu["count"]
        contents = []
        for comment in danmu["comments"]:
            content = check_content(comment["content"], contents)
            if content is None:
                continue
            else:
                contents.append(content)
            if comment["content_style"]:
                style = json.loads(comment["content_style"])
                if style.get("gradient_colors"):
                    color = style["gradient_colors"]
                elif style.get("color"):
                    color = style["color"]
                else:
                    color = ["ffffff"]
            else:
                color = ["ffffff"]
            comments.append([content, color, comment["timepoint"]])
        print("已下载{:.2f}%".format(params["timestamp"]*100/duration))
        params["timestamp"] += 30
    comments = sorted(comments, key=lambda _: _[-1])
    return comments

    
def get_one_subtitle_by_vinfo(vinfo, font="微软雅黑", font_size=25, skip=False):
    vid, name, duration, target_id = vinfo
    print(name, "开始下载...")
    flag, file_path = check_file(name, skip=skip)
    if flag is False:
        print("跳过{}".format(name))
        return
    comments = get_danmu_by_target_id(vid, duration, target_id, font=font, font_size=font_size)
    # print("{}弹幕下载完成！".format(name))
    return comments, file_path

def ask_input(url=""):
    if url == "":
        url = input("请输入vid/coverid/链接，输入q退出：\n").strip()
    if url == "q" or url == "":
        sys.exit("已结束")
    # https://v.qq.com/x/cover/m441e3rjq9kwpsc/i0025secmkz.html
    params = url.replace(".html", "").split("/")
    if params[-1].__len__() == 11:
        vids = [params[-1]]
    elif params[-1].__len__() == 15:
        cid = params[-1]
        vids = get_vids(cid)
    else:
        vid = url.split("vid=")[-1]
        if len(vid) != 11:
            vid = vid.split("&")[0]
            if len(vid) != 11:
                sys.exit("没找到vid")
        vids = [vid]
    return vids
        

def main(args):
    vids = []
    if args.cid and args.cid.__len__() == 15:
        vids += get_vids(args.cid)
    if args.vid:
        if args.vid.strip().__len__() == 11:
            vids += [args.vid.strip()]
        elif args.vid.strip().__len__() > 11:
            vids += [vid for vid in args.vid.strip().replace(" ", "").split(",") if vid.__len__() == 11]
        else:
            pass
    if args.url:
        vids += ask_input(url=args.url)
    if args.vid == "" and args.cid == "" and args.url == "":
        vids += ask_input()
    if vids.__len__() <= 0:
        sys.exit("没有任何有效输入")
    vinfos = get_video_info_by_vid(vids)
    subtitles = {}
    for vinfo in vinfos:
        comments, file_path = get_one_subtitle_by_vinfo(vinfo, args.font, args.font_size, args.y)
        write_one_video_subtitles(file_path, comments, args)
        subtitles.update({file_path:comments})
    return subtitles

# if __name__ == "__main__":
#     # 打包 --> pyinstaller -F .\qq.py -c -n GetDanMu_qq_1.1
#     main()
#     # subtitle = ASS()