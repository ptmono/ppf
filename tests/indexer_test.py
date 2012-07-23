#!/usr/bin/python
# coding: utf-8

from common import *

from indexer import File


# class Comments_test(TestCase):

#     def __init__(self, methodName='runTest'):
#         super(Comments_test, self).__init__(methodName)

#     def test_null_json(self):
        
#         self.assertEqual('aaa', "bbb")


# def test_abc():
#     assert 'a' == 'c'


def test_LockExists():
    """
    How to deal lock file.
    >>> test_LockExists()
    
    """
    doc_id = 1111111111
    file_type = 'a'
    mode = 'w'

    # Lock the file
    file1 = File(doc_id, file_type, mode)
    file1.lock_wait_interval = 0.001
    file1.write('bbc')

    # Will delete lock and backup file
    file2 = File(doc_id, file_type, 'r')
    file2.lock_wait_interval = 0.001
    file2.read()
    file2.close()

    # # Clean test file
    # filename = file1.filename
    # file1._remove()
    # file1.close()
    # assert not os.path.exists(filename)

class File_test(TestCase):
    pass
