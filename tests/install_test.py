from common import *

from tools.uploader import upload_with_config
import config
import os


def test_installing():
    destroy()
    upload_with_config()
    install()
    destroy()

def test_file_permission():
    '''
    We will upload files to FTP with tools/uploader.py the directory of
    database requires the read/write permission of server.

    It is convenient to change the permission of file in client. It means
    that tools/uploader.py will sync the permission.
    '''
    # Upload the web to the server
    destroy()
    upload_with_config()

    # Check writable permission. muses, htmls, comments can be writable by
    # the server.
    # Simply check the permission of others.
    s_database_directory = config.server_root_directory + '/' + config.dbs_d
    s_permission = os.stat(s_database_directory)
    s_permission_with = oct(s_permission.st_mode)[3:]

    c_database_directory = config.root_abpath + config.dbs_d
    c_permission = os.stat(c_database_directory)
    c_permission_with = oct(c_permission.st_mode)[3:]
    assert s_permission_with == c_permission_with

    destroy()
    
