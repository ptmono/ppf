#!/usr/bin/python
# coding: utf-8

from common import *
from unittest import TestCase



from lxml.cssselect import CSSSelector
from lxml.html import parse, fromstring, tostring

from dlibs.logger import logger


from dnews.model import *
from dnews.smodel.torrentrg import TorrentRgModel
from dnews.smodel.torrentrg import _dummy_path as _dummy_path_torrentrg


_dummy_db_path = Var.cur_join("__tmp/session_test.sqlite")

class TorrentRgTestModel(TorrentRgModel):
    url_format = None
    urls = [_dummy_path_torrentrg]


class DummyModel(GetSetModel):
    url_format = 'http://example.com/%s/%s/%s'
    url_range = [range(3), [range(4), range(5, 7)], [range(8)]]
    
    def set_sels(self):
        return ["1", "2"]
        
    def getTitle(self):
        return ["1"]

    def getUrl(self):
        return ["2"]


class DummyModel2(GetSetModel):
    urls = ["http://news.nate.com/recent?mid=n0100&type=c&date=20130610&page=2"]
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

    def getUrl(self):
        result = []
        for s in self._sels:
            result.append(s.get('href'))
        return result

class Test_GetSetModel(TestCase):
    def test_basic(self):
        """
        How to deal url aaa?
        --> in Model or Scraper
        Let' use on both case
        """
        dummy = DummyModel()
        self.assertEqual(dummy._info['columns'], {'url': 'getUrl', 'title': 'getTitle'})
        self.assertEqual(dummy._info['variables'], {'_sels': 'set_sels'})

        dummy2 = DummyModel2()
        self.assertEqual(dummy2._info['urls'], ['http://news.nate.com/recent?mid=n0100&type=c&date=20130610&page=2'])

        # columns
        #self.assertEqual(list(dummy2._info['columns'].keys()), ['url', 'title'])
        #self.assertEqual(dummy2.columns(), ['url', 'title'])

    def test_get(self):
        """

        How to get the result of parse.
        candidate1 -->
        get returns {'col1': ['i1', 'i2', 'i3'], 'col2': ['j1', 'j2', 'j3']}

        candidate2 -->
        3rd party method get(SModel) returns candidate1

        candidate3 -->
        create new class in runtime. New class inherit model.

        """
        dummy = DummyModel2()
        # self.assertEqual(dummy.get('aaa'), {'url': [], 'title': []})
        # import requests
        # data = requests.get('http://news.nate.com/recent?mid=n0100&type=c&date=20130610&page=2').content
        # fd = open('sample_nate.html', 'w')
        # fd.write(data)
        # fd.close()
        fd = open('sample_nate.html', 'rb')
        data = fd.read()
        fd.close()

        if PY3:
            self.assertEqual(str(type(dummy.get(data)['title'][0])), "<class 'str'>")
            self.assertEqual(dummy.get(data)['title'][0], '인사말하는 진영 장관')
        else:
            self.assertEqual(str(type(dummy.get(data)['title'][0])), "<type 'unicode'>")
            self.assertEqual(dummy.get(data)['title'][0], u('인사말하는 진영 장관'))

class Test_libs(TestCase):

    def test_generate_urls(self):
        url_format = 'http://example.com/%s/%s'
        url_range = [[range(4)], [range(1, 7), range(5, 9)]]
        self.assertEqual(list(generate_urls(url_format, url_range)), ['http://example.com/0/1', 'http://example.com/0/2', 'http://example.com/0/3', 'http://example.com/0/4', 'http://example.com/0/5', 'http://example.com/0/6', 'http://example.com/0/5', 'http://example.com/0/6', 'http://example.com/0/7', 'http://example.com/0/8', 'http://example.com/1/1', 'http://example.com/1/2', 'http://example.com/1/3', 'http://example.com/1/4', 'http://example.com/1/5', 'http://example.com/1/6', 'http://example.com/1/5', 'http://example.com/1/6', 'http://example.com/1/7', 'http://example.com/1/8', 'http://example.com/2/1', 'http://example.com/2/2', 'http://example.com/2/3', 'http://example.com/2/4', 'http://example.com/2/5', 'http://example.com/2/6', 'http://example.com/2/5', 'http://example.com/2/6', 'http://example.com/2/7', 'http://example.com/2/8', 'http://example.com/3/1', 'http://example.com/3/2', 'http://example.com/3/3', 'http://example.com/3/4', 'http://example.com/3/5', 'http://example.com/3/6', 'http://example.com/3/5', 'http://example.com/3/6', 'http://example.com/3/7', 'http://example.com/3/8'])

        url_format2 = 'aa/%s/%s/%s'
        url_range2 = [[range(2)], [range(1, 3), range(5, 7)], [range(2), range(4, 6)]]
        self.assertEqual(len(list(generate_urls(url_format2, url_range2))), 32)

        url_range = [['a', 'b'], ['dd', 'yy']]
        self.assertEqual(list(generate_urls(url_format, url_range)), ['http://example.com/a/d', 'http://example.com/a/d', 'http://example.com/a/y', 'http://example.com/a/y', 'http://example.com/b/d', 'http://example.com/b/d', 'http://example.com/b/y', 'http://example.com/b/y'])
    
    def test_product_generator(self):
        url_range = [[range(4)], [range(1, 7), range(5, 9)]]
        self.assertEqual(list(product_generator(url_range)), [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 5), (0, 6), (0, 7), (0, 8), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 5), (1, 6), (1, 7), (1, 8), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 5), (2, 6), (2, 7), (2, 8), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 5), (3, 6), (3, 7), (3, 8)])

        url_range2 = [range(4), [range(1, 7), range(5, 9)]]
        self.assertEqual(list(product_generator(url_range2)), list(product_generator(url_range)))


    def test_merge_lists(self):
        alist = range(8)
        self.assertEqual(list(merge_lists(alist)), [0, 1, 2, 3, 4, 5, 6, 7])

    def test_list_range_to_list(self):
        import types
        url_range = [1, 10]
        url_range2 = [[1, 5]]
        url_range3 = [[1,4], [6, 8], [12, 18]]
        url_range4 = ["a", "b"]

        self.assertEqual(list_range_to_list(url_range), [1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(list_range_to_list(url_range2), [1, 2, 3, 4])
        self.assertEqual(list_range_to_list(url_range3), [1, 2, 3, 6, 7, 12, 13, 14, 15, 16, 17])

        #self.assertEqual(list_range_to_list(url_range4), 888)
        self.assertRaises(ValueError, list_range_to_list, url_range4)


class Dummy_parseAttr:

    def getTitle(self): pass
    def get_Title(self): pass
    def get_title(self): pass
    def get_titleAttr(self): pass


class Test_parseAttr(TestCase):
    def test_basic(self):
        dummy = Dummy_parseAttr()
        self.assertEqual(parseAttr(dummy, "get(\w+)", 1),
                            {'_titleAttr': 'get_titleAttr',
                            '_title': 'get_title',
                            '_Title': 'get_Title',
                            'title': 'getTitle'})
    

class DummyModelNoUrls(GetSetModel):
    def getTitle(self): pass

    
class Test_UrlsMixin(TestCase):
    def test_basic(self):
        tg = TorrentRgTestModel()
        self.assertEqual(tg._info['urls'],
                         ['/home/ptmono/Desktop/Documents/works/0git/dnews/smodel/__tmp/torrentrg_movie.html'])
        
        dummy = DummyModelNoUrls()


class Test_GetMixin(TestCase):
    def infoToList(self):
        dummy = {'col1': ['i1', 'i2', 'i3'], 'col2': ['j1', 'j2', 'j3']}

        self.assertEqual(list(GetMixin.infoToList(dummy)),
                         [('j1', 'i1'), ('j2', 'i2'), ('j3', 'i3')])

    def test_infoToDictList(self):
        dummy = {'col1': ['i1', 'i2', 'i3'], 'col2': ['j1', 'j2', 'j3']}
        self.assertEqual(list(GetMixin.infoToDictList(dummy)),
                         [{'col1': 'i1', 'col2': 'j1'}, {'col1': 'i2', 'col2': 'j2'}, {'col1': 'i3', 'col2': 'j3'}])
