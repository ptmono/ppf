from dlibs.common import *
import os
import sys
# cur_file_path = os.path.abspath(__file__)
# cur_dir_path = os.path.dirname(cur_file_path)
# root_path = os.path.dirname(cur_dir_path)
# if root_path not in sys.path:
#     sys.path.insert(0, root_path)
    
import time
try:
    from urlparse import urlparse
    from urllib import unquote
except ImportError:
    from urllib.parse import urlparse
    from urllib.parse import unquote
from cgi import parse_qs

import requests

from lxml.cssselect import CSSSelector
from lxml.html import parse, fromstring, tostring

from dnews.model import GetSetModel
from dnews.model_tools import CssParsers, NetTools

from dlibs.logger import logger, loggero


import logging
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)


