from common import *
from unittest import TestCase

from dlibs.logger import logger
from dnews.smodel.torrentrg import TorrentRgModel
from dnews.smodel.torrentrg import _dummy_path as _dummy_path_torrentrg

from dnews.scraper import Scraper, MapperClass

from dnews.session import Session

_dummy_data = NetTools.read(_dummy_path_torrentrg)
_dummy_dbname = "sqlite:///__tmp/session_test.sqlite"

class TorrentRgTestModel(TorrentRgModel):
    urls = [_dummy_path_torrentrg]


class Test_Session(TestCase):

    def prepare_db(self):
        scraper = Scraper(TorrentRgTestModel, _dummy_dbname)
        scraper.dododo()
        #self.assertEqual(_dummy_path_torrentrg, 3437)
        
        
    def basic(self):
        session = Session(TorrentRgTestModel, _dummy_dbname)
        session.query()
        
