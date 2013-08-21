from common import *
from unittest import TestCase

from scraper import Scraper, MapperClass

from dlibs.logger import logger


scraper = Scraper(NateBreakingNewsModel2, "sqlite:///natebreaking3.sqlite")
scraper.dododo()
