import sys

import os.path

cur_path = os.path.dirname(os.path.abspath(__file__))
if not cur_path in sys.path:
    sys.path.insert(0, cur_path)


from ppf.app import app as application