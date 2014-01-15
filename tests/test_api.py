#!/usr/bin/python
# coding: utf-8

import os
ope = os.path.exists
from io import open
from unittest import TestCase

from app import app

from common import *

from ppf.indexer import File
from ppf.api import Data
from ppf.tools.post import MuseArticle
from ppf import config

tapp = app.test_client()

class Test_API(TestCase, FileConvenientMixIn):
    @classmethod
    def setUpClass(cls):
        pass
        
    @classmethod
    def tearDownClass(cls):
        pass
    def setUp(self):
        self.dummy_article_doc_id = '9191919191'
        self.dummy_fd = File(self.dummy_article_doc_id, 'a', 'w')
        self.dummy_fd.write(u'#title my migration note to ubuntu 12.04\n#author\n#dalsoo\n#date 1401152021\n\naaaaa')
        self.dummy_filename = self.dummy_fd.filename
        self.dummy_lock_filename = self.dummy_fd.lock_filename
        self.dummy_backup_filename = self.dummy_fd.backup_filename
        self.dummy_fd.close()
        self.assertTrue(ope(self.dummy_filename))

        self.assertEqual(self.dummy_fd.filename, 7926)

    def tearDown(self):
        self.removeFiles(self.dummy_fd)

    def test_writeArticle(self):
        base64_content = Data.encode_base64('content')
        data = {'cmd': 'writeArticle',
            'doc_id': '9999999999',
            'secure_key': config.SECURE_KEY,
            '_base64_content': base64_content}

        rv = tapp.post('api', data=data)
        self.assertEqual(rv.status_code, 200)
        self.assertTrue(rv.data, 'ok')

        dummy_path = config.article_filename('9999999999')
        filep = ope(dummy_path)
        self.assertTrue(filep)
        if filep: os.remove(dummy_path)

    def updateIndex(self):
        mu = MuseArticle(self.dummy_article_doc_id)
        _jsonBase64_dict = mu.json
        data = {'cmd': 'updateIndex',
                'doc_id': self.dummy_article_doc_id,
                '_jsonBase64_dict': _jsonBase64_dict}
        rv = tapp.post('api', data=data)
        self.assertEqual(rv.status_code, 200)

    def comment(self):
        comment_content = Data.encode_base64(u'comment_content')
        comment_name = Data.encode_base64(u'ptmono')
        data_for_no_article = {'cmd': 'writeComment',
                'doc_id': '9292919191',
                '_base64_content': comment_content,
                'secure_key': config.SECURE_KEY,
                '_base64_name': comment_name,
                'password': ''}

        data = {'cmd': 'writeComment',
                'doc_id': self.dummy_article_doc_id,
                '_base64_content': comment_content,
                'secure_key': config.SECURE_KEY,
                '_base64_name': comment_name,
                'password': ''}
        comment_path = os.path.join(config.comments_d, self.dummy_article_doc_id + config.comment_extension)
                    
        rv = tapp.post('api', data=data_for_no_article)
        self.assertEqual(rv.status_code, 500)
        dummy_comment_path = os.path.join(config.comments_d, '9292919191' + config.comment_extension)
        filep = ope(dummy_comment_path)
        self.assertFalse(filep)

        rv = tapp.post('api', data=data)
        self.assertEqual(rv.status_code, 200)
        filep = ope(comment_path)
        self.assertTrue(filep)
        
