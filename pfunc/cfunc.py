#!/usr/bin/env python3.7
# coding=utf-8
'''
# 作者: weimo
# 创建日期: 2020-01-05 12:45:18
# 上次编辑时间       : 2020-01-16 14:50:34
# 一个人的命运啊,当然要靠自我奋斗,但是...
'''

import hashlib
from urllib.parse import urlparse

from basic.vars import ALLOW_SITES

def remove_same_danmu(comments: list):
    # 在原有基础上pop会引起索引变化 所以还是采用下面这个方式
    contents = []
    for comment in comments:
        content, color, timepoint = comment
        content = content.replace(" ", "")
        if content in contents:
            continue
        else:
            contents.append([content, color, timepoint])
    return contents

def check_url_site(url):
    site = urlparse(url).netloc.split(".")[-2]
    if site in ALLOW_SITES:
        return site
    else:
        return None

def check_url_locale(url):
    flag = {
        "cn":"zh_cn",
        "tw":"zh_tw",
        "intl":"intl"
    }
    if urlparse(url).netloc.split(".")[0] == "tw":
        return flag["tw"]
    else:
        return flag["cn"] 

def yk_msg_sign(msg: str):
    return hashlib.new("md5", bytes(msg + "MkmC9SoIw6xCkSKHhJ7b5D2r51kBiREr", "utf-8")).hexdigest()

def yk_t_sign(token, t, appkey, data):
    text = "&".join([token, t, appkey, data])
    return hashlib.new('md5', bytes(text, 'utf-8')).hexdigest()