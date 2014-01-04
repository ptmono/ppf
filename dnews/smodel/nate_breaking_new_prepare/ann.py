from common import *
from scraper import Scraper, MapperClass

import requests

nb = NateBreakingNewsModel()

data = requests.get(nb.urls[0]).content

aa = nb.get(data)
dd = nb.getTitle()
for a in dd:
    print a

print len(dd)

cc = nb.getUrl()
for c in cc:
    print c
print len(cc)


dd = nb.getSummary()
for d in dd:
    print d
print len(dd)

ee = nb.getMedia()
for e in ee:
    print e
print len(ee)

