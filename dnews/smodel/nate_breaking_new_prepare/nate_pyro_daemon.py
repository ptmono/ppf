from dlibs.common import *

import Pyro4

from common import *

from nate import scrap
from nate_config import daemon1_uri_path, daemon2_uri_path


class Cralwer(object):
    @class
    def scrap(self, date):
        scrap(date)


def write_uri(uri, path):
    fd = open(path, 'w')
    fd.write(uri)
    fd.close()


greeting_scrap1=Crawler()
greeting_scrap2=Crawler()


daemon1 = Pyro4.Daemon()
daemon2 = Pyro4.Daemon()
# daemon3 = Pyro4.Daemon()
# daemon4 = Pyro4.Daemon()
# daemon5 = Pyro4.Daemon()
uri1 = daemon1.register(greeting_scrap1)
uri2 = daemon2.register(greeting_scrap2)
write_uri(uri1.asString(), daemon1_uri_path)
write_uri(uri1.asString(), daemon2_uri_path)

