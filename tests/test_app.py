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
        

    def is_page_ok(self, uri):
        rv = self.app.get(uri)
        self.assertTrue(rv.data)
        self.assertEquals(rv.status_code, 200)
