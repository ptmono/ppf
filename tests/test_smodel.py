#!/usr/bin/python
# coding: utf-8

from unittest import TestCase

from common import *

from dnews.smodel.torrentrg import TorrentRgModel
from dnews.smodel.torrentrg import _dummy_path as _dummy_path_torrentrg

from dnews.smodel.saramin import SaraminIt, SaraminItTest


"""

Guide
=====

Test the model in smodel directory. You should create dummy html as
_dummy_path variable.

Finally test the result in tests.


"""


dummy_data_torrentrg = NetTools.read(_dummy_path_torrentrg)

class Test_TorrentRgModel(TestCase):
    def test_basic(self):
        tr = TorrentRgModel()
        dd = tr.get(dummy_data_torrentrg)
        self.assertEqual(len(dd['num']), 30)
        self.assertEqual(len(dd['title']), 30)
        self.assertEqual(len(dd['url']), 30)


class Test_SaraminItTitles(TestCase):
    def test_basic(self):
        data = SaraminItTest._dummy_data()
        sit = SaraminIt()
        dd = sit.get(data)
        
        self.assertEqual(len(dd['title']), 30)
        self.assertEqual(len(dd['date']), 30)
        self.assertEqual(len(dd['idx']), 30)
        self.assertEqual(len(dd['corpidx']), 30)
        
