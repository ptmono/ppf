#!/usr/bin/python
# coding: utf-8

from common import *
from unittest import TestCase

from dnews.scraper import Scraper, MapperClass

from dlibs.logger import logger

class Test_Scraper(TestCase):

    def basics(self):
        
        scraper = Scraper(NateBreakingNewsModel, "nate_news.sqlite")
        scraper.dododo()

    def test_get(self):
        scraper = Scraper(NateBreakingNewsModel, "sqlite:///__tmp/natebreaking.sqlite")
        
        #scraper.get()

        scraper.dododo()
        self.assertEqual(scraper.session.query(scraper.mapped_class).all()[0].title, u('역발상'))



    def test_get2(self):
        scraper = Scraper(NateBreakingNewsModel2, "sqlite:///__tmp/natebreaking3.sqlite")
        scraper.dododo()

    def show2(self):
        scraper = Scraper(NateBreakingNewsModel2, "sqlite:///natebreaking2.sqlite")
        orms = scraper.session.query(scraper.mapped_class).all()
        for orm in orms:
            logger().debug(orm.title)


class TestMethodModel(GetSetModel):
    url_format = "aa%sbb%s"
    url_range = [[range(3)], [range(6, 9)]]
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
            

class NateBreakingNewsModelForThread(GetSetModel):
    url_format = "http://news.nate.com/recent?mid=n0100&type=c&date=%s&page=%s"
    url_range = [[range(20130610, 20130616)], [range(2, 20)]]
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

    
class Test_Scraper_methods(TestCase):
    @classmethod
    def setUpClass(cls):
        thread_db = '__tmp/natebreaking.sqlite'
        if os.path.exists(thread_db):
            os.remove(thread_db)

    @classmethod
    def tearDownClass(cls):
        pass

    def thread(self):
        scraper = Scraper(TestMethodModel, "sqlite:///natebreaking.sqlite", thread=4)
        self.assertEqual(scraper._dododo_thread(), 3081)

    def thread(self):
        scraper = Scraper(NateBreakingNewsModelForThread, "sqlite:///__tmp/natebreaking.sqlite", thread=4)
        scraper.dododo()

        orms = scraper.session.query(MapperClass).all()
        self.assertEqual(len(orms), 560)


class Test_Worker(TestCase):
    pass
