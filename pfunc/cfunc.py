#!/usr/bin/env python3.7
# coding=utf-8
'''
# 作者: weimo
# 创建日期: 2020-01-05 12:45:18
# 上次编辑时间: 2020-01-05 14:44:42
# 一个人的命运啊,当然要靠自我奋斗,但是...
'''
from urllib.parse import urlparse


def check_url_site(url):
    return urlparse(url).netloc.split(".")[-2]

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