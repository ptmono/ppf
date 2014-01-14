import os, sys
import shutil

from dlibs.libs import add_sys_path
ROOT_PATH = add_sys_path(__file__, subpath=True)

from unittest import TestCase
from ppf.tools.uploader import Uploader, UploadInfoFromConfig

import ppf.config
from ppf.install import init_db

try:
    from twill import get_browser
except:
    pass


class Var:
    dummy_id = '9999999999'
    dummy_muse = '9999999999.muse'
    dummy_html = '9999999999.html'


def install():
    url_install = ppf.config.url_root + "install.py"
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

    fd = file(ppf.config.muses_d + Var.dummy_muse, 'w')
    fd.write(muse)
    fd.close()

    fd = file (ppf.config.htmls_d + Var.dummy_html, 'w')
    fd.write(html)
    fd.close()
    

def destroy():
    '''
    >>> destroy() #doctest: +SKIP
    /... is deleted
    >>> import os.path
    >>> os.path.exists(ppf.config.server_root_directory) #doctest: +SKIP
    False
    '''
    # Delete installed files
    shutil.rmtree(ppf.config.server_root_directory, ignore_errors=True)
    print("%s is deleted" % ppf.config.server_root_directory)

    # Delete dummy article
    try:
        os.remove(ppf.config.htmls_d + Var.dummy_html)
        os.remove(ppf.config.muses_d + Var.dummy_muse)
    except OSError:
        pass

    # Init index.json
    #init_db()
