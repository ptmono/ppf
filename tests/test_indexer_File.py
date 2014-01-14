#!/usr/bin/python
# coding: utf-8


import os
ope = os.path.exists
from io import open
from unittest import TestCase

from common import *
from ppf.indexer import File


class FileConvenientMixIn(object):

    def getFiles(self, file):
        return [file.filename, file.lock_filename, file.backup_filename]

    def fileExistsp(self, file):
        for f in self.getFiles(file):
            self.assertTrue(ope(f))

    def fileNotExistsp(self, file):
        for f in self.getFiles(file):
            self.assertFalse(ope(f))

    def removeFiles(self, file):
        for f in self.getFiles(file):
            if os.path.exists(f):
                os.remove(f)
            
        
class Test_File(TestCase, FileConvenientMixIn):
    @classmethod
    def setUpClass(cls):
        cls.dummy_doc_id = '9999889999'
        cls.dummy_file = File(cls.dummy_doc_id, 'a', 'w')
        cls.dummy_file.write(u'aaa')
        cls.dummy_file.close()        
        
    @classmethod
    def tearDownClass(cls):
        cls.dummy_file._remove()

    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_write_article(self):
        dummy_doc_id = '9191919191'
        file = File(dummy_doc_id, 'a', 'w')
        file.write(u'aaa')
        file.close()

        file_read = File(dummy_doc_id, 'a', 'r')
        content = file_read.read()
        self.assertEqual(content, u'aaa')

        self.removeFiles(file)
        self.fileNotExistsp(file)

    def test_write_comment(self):
        dummy_doc_id = '9191919191'
        pass

