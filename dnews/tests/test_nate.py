#!/usr/bin/python
# coding: utf-8

from unittest import TestCase

from common import *
from dnews.smodel.nate_breaking_news import latest_page, detect_latest_page


class Test_Methods(TestCase):
    @classmethod
    def setUpClass(cls):
        pass
    @classmethod
    def tearDownClass(cls):
        pass
    def setUp(self):
        pass
    def tearDown(self):
        pass

    # Obsolete. Use latest_page
    def detect_latest_page(self):
        # date=20130802&page=1333 is the latest
        bb = detect_latest_page(20130802)
        self.assertEqual(bb, 1437)

        # date=20130723&page=1591
        # bb = detect_latest_page(20130723)
        # self.assertEqual(bb, 1499)
        

        
