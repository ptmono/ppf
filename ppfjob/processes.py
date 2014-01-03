#!/usr/bin/env python
# coding: utf-8
import os

from dlibs.common import *

from .search_saramin			import KeywordInfos, keyword_search
from .tools				import File


class KeywordsInfo(dict):
    def exclude(self, infos):
        pass


class PreviousInfo(dict):
    pass

class Var:
    prev_infos = {}


def init():
    readPreviousInfos()
    
def readPreviousInfos():
    keywords_prev_idxs_path = 'data/keywords_prev_idxs.pickle'
    try:
        fd = File(keywords_prev_idxs_path, 'r')
        Var.prev_infos = fd.read()
        fd.close()
    except FileNotFoundError:
        fd = File(keywords_prev_idxs_path, 'w')
        fd.write('')
        fd.close()
        Var.prev_info = ''


def keywords_search(keywords):
    pass

def _keywords_search(infos):
    pass
