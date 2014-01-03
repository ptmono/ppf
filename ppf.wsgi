import sys
import os

import os.path

cur_path = os.path.dirname(os.path.realpath(__file__))
if not cur_path in sys.path:
    sys.path.insert(0, cur_path)
    sys.path.insert(0, os.path.join(cur_path, 'modules'))

from ppf.app import app as application
