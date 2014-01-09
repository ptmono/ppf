import os, sys

from dlibs.libs import add_sys_path
ROOT_PATH = add_sys_path(__file__, subpath=True)

sys.path.insert(0, '/home/ptmono/works/0git/dScraper')

from unittest import TestCase

def data_path(filename):
    return os.path.join('data', filename)
