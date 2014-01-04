from common import *
from unittest import TestCase

from dnews.scraper import Scraper, MapperClass

from dlibs.logger import logger


class NateBreakingNewsModel(GetSetModel):
    url_format = "http://news.nate.com/recent?mid=n0100&type=c&date=%s&page=%s"
    url_range = [[range(20130610, 20130615)], [range(3, 8)]]
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




class Test_Scraper(TestCase):

    def basic(self):
        scraper = Scraper(NateBreakingNewsModel, "sqlite:///natebreaking.sqlite", thread=2)
        self.assertEqual(scraper.dododo(), 8936)
        
