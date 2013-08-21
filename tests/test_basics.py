#!/usr/bin/python
# coding: utf-8

from common import *
from unittest import TestCase

from lxml.cssselect import CSSSelector
from lxml.html import parse, fromstring, tostring

from dnews.test_model import DummyModel2

GetSetModel = object
GetSetSelectorModel = object
GetRegexpSingleModel = object

class NateBreakingNews(GetSetModel):
    def set_sels(self):
        selector = ('ul[class="mduSubject"] a')
        sel = CSSSelector(selector)
        sel_list = sel(fromstring(self.container.source))
        return sel_list
        
    def getTitle(self):
        result = []
        for s in self._sels:
            title = s.text.strip()
            result.append(title)
        return result

    def getUrl(self):
        result = []
        for s in self._sels:
            result.append(s.get('href'))
        return result
    

class NageBreakingNews2(GetSetSelectorModel):
    def set_sels(self):
        "Returns source"
        return 'ul[class="mduSubject"] a'

    def getTitle(self):
        "Parse self._sels. And returns a list."

    def getUrl(self):
        "Parse self._sels. And returns a list."

    
class NateBreakingNews3(GetRegexpSingleModel):
    """
    set: Returns source

    get: 
    
    """
    def set_sels(self):
        "Returns source"
        return 'ul[class="mduSubject"] a'

    def getTitle(self):
        "Returns regexp which returns title"

    def getUrl(self):
        "Returns regexp which returns title"


class Test_Basics(TestCase):
    def basics(self):

        # Sample 1
        crawler = Scraper(DummyModel2, "/tmp/newsdb.sqlite3")
        # crawler.setDb = "sqlite3"
        # crawler.setModel = Smodel
        # crawler.threading = True
        crawler.dododo()

        
