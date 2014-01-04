#!/usr/bin/python
# coding: utf-8

from common import *
from unittest import TestCase

from scraper import Scraper, MapperClass

from nate import NateBreakingNewsModel2

def basic():
    """

    >>> scraper = Scraper(NateBreakingNewsModel2, "sqlite:///nate/natebreaking20130621.sqlite")
    >>> orms = scraper.session.query(MapperClass).all()
    >>> for i in range(3):
    ...     print(orms[i].title)
    
    """

