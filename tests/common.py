import os, sys
import shutil
cur_file_path = os.path.abspath(__file__)
cur_dir_path = os.path.dirname(cur_file_path)
root_path = os.path.dirname(cur_dir_path)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from unittest import TestCase
from tools.uploader import Uploader, UploadInfoFromConfig

import config
import libs
from install import init_db

from twill import get_browser


class Var:
    dummy_id = '9999999999'
    dummy_muse = '9999999999.muse'
    dummy_html = '9999999999.html'


def install():
    url_install = config.url_root + "install.py"
    b = get_browser()
    b.go(url_install)

def init():
    '''
    Upload and Create dummy files.
    '''
    # Upload files to server.
    uploader = Uploader(UploadInfoFromConfig)
    uploader.upload()

    # Create dummy article
    cdir = cur_dir_path + "/"

    fd = file(cdir + Var.dummy_muse, 'r')
    muse = fd.read()
    fd.close()

    fd = file(cdir + Var.dummy_html, 'r')
    html = fd.read()
    fd.close()

    fd = file(config.muses_d + Var.dummy_muse, 'w')
    fd.write(muse)
    fd.close()

    fd = file (config.htmls_d + Var.dummy_html, 'w')
    fd.write(html)
    fd.close()
    

def destroy():
    '''
    >>> destroy() #doctest: +ELLIPSIS
    /... is deleted
    >>> import os.path
    >>> os.path.exists(config.server_root_directory)
    False
    '''
    # Delete installed files
    shutil.rmtree(config.server_root_directory, ignore_errors=True)
    print "%s is deleted" % config.server_root_directory

    # Delete dummy article
    try:
        os.remove(config.htmls_d + Var.dummy_html)
        os.remove(config.muses_d + Var.dummy_muse)
    except OSError:
        pass

    # Init index.json
    init_db()
