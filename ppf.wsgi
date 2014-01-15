import sys
import os

import os.path

cur_path = os.path.dirname(os.path.realpath(__file__))
if not cur_path in sys.path:
    sys.path.insert(0, "/home/ptmono/.local/lib/python3.3/site-packages")
    sys.path.insert(0, cur_path)
    sys.path.insert(0, os.path.join(cur_path, 'modules'))
    sys.path.insert(0, "/home/ptmono/works/0git/dnews")
    sys.path.insert(0, "/home/ptmono/works/0git/dScraper")
    sys.path.insert(0, "/home/ptmono/works/0git/dlibs")
    sys.path.insert(0, "/home/ptmono/works/0git/dfilter")

from app import app as application
