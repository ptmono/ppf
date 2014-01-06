#!/usr/bin/python
# coding: utf-8

"""

Using dummy
===========

 - NetTools.read(DummyModel.urls[0]) provides the html source.
 - Var.read_dummy_info
 - Var.read_dummy_list


"""



import sys
import pickle
import os.path
sys.path.append("../../")

from lxml.cssselect import CSSSelector
from lxml.html import parse, fromstring, tostring

from dlibs.common import *
from unittest import TestCase

from dnews.model import GetSetModel
from dnews.model_tools import CssParsers, NetTools, TestingMixin

from dnews.smodel.torrentrg import TorrentRgModel
from dnews.smodel.torrentrg import _dummy_path as _dummy_path_torrentrg




class NateBreakingNewsModel(GetSetModel):
    urls = ["http://news.nate.com/recent?mid=n0100&type=c&date=20130610&page=2"]
    def set_sels(self):
        selector = ('dl[class="mduSubjectContent"]')
        sel = CSSSelector(selector)
        sel_list = sel(fromstring(self.source))
        return sel_list
        
    def getTitle(self):
        result = []
        selector = ('a strong')
        sel_sub = CSSSelector(selector)
        for sel in self._sels:
            sel_list = sel_sub(sel)
            title = sel_list[0].text_content()
            result.append(title)
        return result

    def getSummary(self):
        result = []
        selector = ('dd a')
        sel_sub = CSSSelector(selector)
        for sel in self._sels:
            sel_list = sel_sub(sel)
            summary = sel_list[0].text_content().strip()
            result.append(summary)
        return result
    
    def getUrl(self):
        result = []
        selector = ('a')
        sel_sub = CSSSelector(selector)
        for sel in self._sels:
            sel_list = sel_sub(sel)
            result.append(sel_list[0].get('href'))
        return result

    def getMedia(self):
        result = []
        selector = ('span[class="medium"]')
        sel_sub = CSSSelector(selector)
        for sel in self._sels:
            sel_list = sel_sub(sel)
            media = sel_list[0].text.strip()
            result.append(media)
        return result


class NateBreakingNewsModel(GetSetModel):
    url_format = "http://news.nate.com/recent?mid=n0100&type=c&date=%s&page=%s"
    url_range = [[20130610], [1]]
    def set_sels(self):
        selector = ('dl[class="mduSubjectContent"] a')
        sel = CSSSelector(selector)
        sel_list = sel(fromstring(self.source))
        return sel_list
        
    def getTitle(self):
        result = []
        for sel in self._sels:
            title = sel.text_content()
            result.append(title)
        return result

    def getContent(self):
        return ['' for i in range(len(self._sels))]

    
    def getUrl(self):
        result = []
        for s in self._sels:
            result.append(s.get('href'))
        return result


    
#Notice: This is test model. so it has not correct parser
class NateBreakingNewsModel2(GetSetModel):
    url_format = "http://news.nate.com/recent?mid=n0100&type=c&date=%s&page=%s"
    url_range = [[20130610], [1]]
    def set_sels(self):
        selector = ('dl[class="mduSubjectContent"] a')
        sel = CSSSelector(selector)
        sel_list = sel(fromstring(self.source))
        return sel_list
        
    def getTitle(self):
        result = []
        for sel in self._sels:
            title = sel.text_content()
            result.append(title)
        return result

    def getContent(self):
        return ['' for i in range(len(self._sels))]

    
    def getUrl(self):
        result = []
        for s in self._sels:
            result.append(s.get('href'))
        return result

class DummyModel(TorrentRgModel):
    urls = [_dummy_path_torrentrg]
    

_cur_file_path = os.path.realpath(__file__)
_cur_dir_path = os.path.dirname(_cur_file_path)
_root_path = os.path.dirname(_cur_dir_path)
    
class Var:
    """
    >>> Var.cur_join("aa")

    >>> assert(Var.read_dummy_info())
    >>> assert(Var.read_dummy_list())

    """
    cur_path = _cur_dir_path
    tmp_path = os.path.join(_cur_dir_path, "__tmp")
    dummy_info_path = os.path.join(_cur_dir_path, "__tmp/DummyModel_info.pickle")
    dummy_list_path = os.path.join(_cur_dir_path, "__tmp/DummyModel_list.pickle")

    @staticmethod
    def cur_join(path):
        return os.path.join(Var.cur_path, path)

    @staticmethod
    def read_dummy_info():
        fd = open(Var.dummy_info_path, 'rb')
        return pickle.load(fd)

    @staticmethod
    def read_dummy_list():
        fd = open(Var.dummy_list_path, 'rb')
        return pickle.load(fd)

        

def __create_dummy():
    """

    >>> #__create_dummy()

    """
    data = NetTools.read(DummyModel.urls[0])
    model = DummyModel()
    info = model.get(data)
    info_list = model.list(data)

    fd = open(Var.dummy_info_path, 'wb')
    pickle.dump(info, fd, protocol=2, fix_imports=True)
    fd.close()

    fd = open(Var.dummy_list_path, 'wb')
    pickle.dump(info_list, fd, protocol=2, fix_imports=True)
    fd.close()

