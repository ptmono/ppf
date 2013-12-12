#!/usr/bin/env python
# coding: utf-8

from common import *

import ppf
from ppf.app import app

class TestApp(TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_home_page_works(self):
        self.is_page_ok('/')
        
    def test_article_doc_page_works(self):
        self.is_page_ok('/article/0000000001')

    def test_article_all_works(self):
        self.is_page_ok('/all')
        self.is_page_ok('/article/all')        


    def write_comment(self):
        data = {'doc_id': '0000000001',
                'content': 'test'}

        rv = self.app.post('/writecomment', data=data)        
        self.assertEqual(rv.data, 3221)


    def test_PageNotFound(self):
        rv = self.app.get('/article/1111111119')
        self.assertEqual(rv.status_code, 404)
        self.assertEqual(rv.data, '{\n  "message": "1111111119"\n}')

    def is_page_ok(self, uri):
        rv = self.app.get(uri)
        self.assertTrue(rv.data)
        self.assertEquals(rv.status_code, 200)


class Test_app_exceptions(TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_PageNotFound(self):
        rv = self.app.get('/article/1111111119')
        self.assertEqual(rv.status_code, 404)
        self.assertEqual(rv.data, '{\n  "message": "1111111119"\n}')
