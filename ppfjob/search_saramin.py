#!/usr/bin/env python
# coding: utf-8

from dnews.smodel.saramin		import SaraminItSearch
from dnews.model_tools			import NetTools
from dlibs.common			import *
from dlibs.logger			import loggero

import re
import os
import time
import copy
import requests
from lxml				import etree

from .tools				import File

try:
    from urllib.parse			import quote
except:
    from urllib				import quote


class KeywordInfos(list):
    '''To deal [{}, {} ...].
    '''
    def values(self, key):
        result = []
        for ele in self:
            result.append(ele[key])
        return result

    def keys(self):
        result = list(self[0].keys())
        result.sort()
        return result

    def exclude(self, key, values):
        """Returns a tuple include two list. First is the duplicated values.
        Second is the values which is not contained in object.

        """
        dummy = copy.deepcopy(self)
        will_be_remove = []
        will_be_droped_idx = copy.deepcopy(values)
        count = 0
        for ele in self:
            if ele[key] in values:
                will_be_remove.append(count)
                will_be_droped_idx.remove(ele[key])
            count += 1

        will_be_remove.sort()
        will_be_remove.reverse()
        for a in will_be_remove:
            dummy.pop(a)
        return dummy, will_be_droped_idx

    
def determine_urls(url):
    source = NetTools.read(url)
    tree = etree.HTML(source)
    tree_list = tree.xpath('//span[@class="goto-num"]')

    try:
        amount = tree_list[0].text
    except IndexError:
        loggero().info("We couldn't find search result.")
        return []
        
    try:
        amount = re.match(".* ([0-9]*).*", amount).group(1)
    except AttributeError:
        loggero().info("We couldn't find search result.")
        return []

    amount = int(amount)

    count = int(amount/80)
    remain = amount%80
    if remain:
        count = count + 1

    result = []
    for a in range(1, count + 1):
        aurl = url.replace('page/1', 'page/'+str(a))
        result.append(aurl)

    return result


def keyword_search(keyword):
    url = 'http://www.saramin.co.kr/zf_user/search/jobs/page/1?pageCount=80&multiLine=&searchword=%s&company_cd=1&area=&domestic=&oversee=&jobCategory=&jobType=&career=&order=&periodType=&period=&condition=&arange=&company=&employ=&rSearchword=&hSearchword=&hInclude=&hExcept='

    keyword = keyword.encode('euc-kr')
    url = url % quote(keyword)
    loggero().info(url)

    urls = determine_urls(url)

    result = KeywordInfos()
    
    for url in urls:
        data = NetTools.read(url).decode('euc-kr')
        obj = SaraminItSearch()
        info = obj.dictlist(data)
        result += info

    return result


