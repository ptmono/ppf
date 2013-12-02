#!/usr/bin/python
# coding: utf-8

from common import *

from tools.uploader import uploadFile

def test_uploadFile():

    init()
    # Create dummy files to be uploaded
    dummy_name = 'dummy_upload.file'
    dummy_path = config.files_d + dummy_name
    fd = file(dummy_path, 'w')
    fd.write('dummy')
    fd.close()

    dummy2_name = 'dummy.py'
    dummy2_path = config.root_abpath + dummy2_name
    fd = file(dummy2_path, 'w')
    fd.write('dummy')
    fd.close()

    try:
        uploadFile('no_file')
        assert False
    except OSError:
        pass

    # Check absolute path
    # The path of dummy in server
    dummy_server_path = config.server_root_directory + '/files/' + dummy_name
    uploadFile(dummy_path)
    assert os.path.exists(dummy_server_path) == True
    os.remove(dummy_server_path)

    # Check related path.
    dummy_repath = 'files/' + dummy_name
    uploadFile(dummy_repath)
    assert os.path.exists(dummy_server_path) == True
    os.remove(dummy_server_path)


    # Root directory uploading
    # Check absolute path
    dummy2_server_path = config.server_root_directory + '/' + dummy2_name
    uploadFile(dummy2_path)
    assert os.path.exists(dummy2_server_path) == True
    os.remove(dummy2_server_path)

    # Check related path
    uploadFile(dummy2_name)     # 'dummy.py'
    assert os.path.exists(dummy2_server_path) == True
    os.remove(dummy2_server_path)

    # Remove client side dummies
    os.remove(dummy_path)
    os.remove(dummy2_path)
    destroy()

