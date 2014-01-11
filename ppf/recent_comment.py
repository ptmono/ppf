#!/usr/bin/python
# coding: utf-8

from .indexer import Comment, File
from . import config

import struct
import random


class CommentPointer(object):
    """

    >>> start_pointer = 4
    >>> max_num = 30
    >>> cp = CommentPointer(start_pointer, max_num)

    >>> cp.items() 			#doctest: +SKIP
    >>> cp.next() 			#doctest: +SKIP

    >>> for a in cp: print a		#doctest: +ELLIPSIS
    4
    ...
    29
    0
    1
    2
    3

    >>> cp.current()
    4
    >>> cp.next()               # Fixme: 5 be returned.
    4
    >>> cp.current()
    5
    >>> cp.init()

    >>> cp.getPointers()		#doctest: +ELLIPSIS
    [4, ... 29, 0, 1, 2, 3]

    >>> cp[5:]				#doctest: +ELLIPSIS
    [9, ... 1, 2, 3]


    >>> cp = CommentPointer(0, max_num)
    >>> for a in cp: print a		#doctest: +ELLIPSIS
    0
    1
    ...
    28
    29

    """

    def __init__(self, start, max_num):
        self.__start = start
        self.max_num = max_num
        self.init()

    def init(self):
        self.startp = True      # True if self.__start is self.__current
        self.__current = self.__start

    def __iter__(self):
        return self

    # Fixme: It returns previous pointer. How to returns current pointer ?
    def next(self):
        "Returns previous pointer."
        if self.__current is self.__start:
            if self.startp:
                self.startp = False
            else:
                self.startp = True
                raise StopIteration

        if self.__current is (self.max_num - 1):
            self.__current = 0
            return self.max_num - 1

        self.__current += 1
        return (self.__current - 1)


    def getPointers(self, key=None):
        result = []
        for a in self:
            result.append(a)
        return result

    def __getitem__(self, key):
        pointers = self.getPointers()
        return pointers[key]

    def current(self):
        return self.__current



# TODO: To use algorithm such like B-tree is more flexiable. But the
# purpose is not require that.
class RecentComments(object):
    """
    We use the file 'comment_order_db' to find recently comments.
    The structure of 'comment_order_db'
     - starting_point	# unsigned char
     - {document_id, comment_number}	# unsigned long long
     - repeat for MAX_KEY_NUMBER

     The size is fixed. KEY_SIZE.

     The order of comments is started from the value of starting_point. We
     can seek the latest comment with (starting_point * KEY_SIZE + 1).

    >>> RecentComments.create_test_file()

    >>> comment = Comment()
    >>> comment.doc_id = '1109012200'
    >>> comment.comment_id = '11'
    >>> comment.title = 'ttitle'
    >>> comment.date = '32'
    >>> comment.content = 'ccontent'

    >>> doc_id = 1110071142
    >>> comment_num = 4
    >>> rcomment = RecentComments(doc_id, comment_num)

    >>> rcomment.start_pointer
    5

    >>> rcomment.all()
    [(1110071144, 5), (1110071145, 6), (1110071146, 7), (1110071147, 8), (1110071148, 9), (1110071149, 10), (1110071150, 11), (1110071151, 12), (1110071152, 13), (1110071153, 14), (1110071154, 15), (1110071155, 16), (1110071156, 17), (1110071157, 18), (1110071158, 19), (1110071159, 20), (1110071160, 21), (1110071161, 22), (1110071162, 23), (1110071163, 24), (1110071164, 25), (1110071165, 26), (1110071166, 27), (1110071167, 28), (1110071168, 29), (1110071139, 0), (1110071140, 1), (1110071141, 2), (1110071142, 3), (1110071143, 4)]

    >>> rcomment.recent()
    [(1110071144, 5), (1110071145, 6), (1110071146, 7), (1110071147, 8), (1110071148, 9), (1110071149, 10), (1110071150, 11), (1110071151, 12), (1110071152, 13), (1110071153, 14), (1110071154, 15), (1110071155, 16), (1110071156, 17), (1110071157, 18), (1110071158, 19), (1110071159, 20), (1110071160, 21), (1110071161, 22), (1110071162, 23), (1110071163, 24), (1110071164, 25), (1110071165, 26), (1110071166, 27), (1110071167, 28), (1110071168, 29), (1110071139, 0), (1110071140, 1), (1110071141, 2), (1110071142, 3), (1110071143, 4)]

    >>> rcomment.get(6) #doctest: +SKIP

    >>> c_order._test_struct_unpack() #doctest: +SKIP

    >>> doc_id = 1110071157
    >>> comment_num = 18
    >>> rrcomment = RecentComments(doc_id, comment_num)
    >>> #rrcomment.recent()
    [(1110071144, 5), (1110071145, 6), (1110071146, 7), (1110071147, 8), (1110071148, 9), (1110071149, 10), (1110071150, 11), (1110071151, 12), (1110071152, 13), (1110071153, 14), (1110071154, 15), (1110071155, 16), (1110071156, 17)]
    >>> #rrcomment.recent()
    [(1110071144, 5), (1110071145, 6), (1110071146, 7), (1110071147, 8), (1110071148, 9), (1110071149, 10), (1110071150, 11), (1110071151, 12), (1110071152, 13), (1110071153, 14), (1110071154, 15), (1110071155, 16), (1110071156, 17)]

    # >>> rrcomment.add(1111111111, 5)
    # >>> rrcomment.recent()

    #>>> rrcomment.recent()

    >>> rcomment = RecentComments()
    >>> rcomment.start_pointer = 30
    >>> rcomment.recent()
    """

    order_db = config.recent_comment_filename()	# DB filename
    STARTING_POINTER_SIZE = 1			# unsigned char
    KEY_SIZE = 8	                	# unsigned long long
    MAX_KEY_NUMBER = 30

    def __init__(self, previous_doc_id=None, previous_comment_num=None):
        """
        We want to get the list of recent comment. The start of the list
        determinded by both PREVIOUS_DOC_ID and PREVIOUS_COMMENT_NUM
        argument.
        """
        self.previous_latest_doc_id = previous_doc_id
        self.previous_latest_comment_num = previous_comment_num
        self.fd = file(self.order_db, 'r')
        self.start_pointer = self.getStartPointer()

        self.cpointer = CommentPointer(self.start_pointer, self.MAX_KEY_NUMBER)

        #self.comments = self.comments()

    def recent(self):
        result = []
        for pointer in self.cpointer:
            seek_pointer = pointer * self.KEY_SIZE + 1
            self.fd.seek(seek_pointer)
            db = self._unpack(self.fd.read(self.KEY_SIZE))
            d_id, c_num = db
            if d_id == self.previous_latest_doc_id and c_num == self.previous_latest_comment_num:
                return result
            result.append(db)
        return result


    def all(self):
        result = []
        for pointer in self.cpointer:
            seek_pointer = pointer * self.KEY_SIZE + 1
            self.fd.seek(seek_pointer)
            db = self._unpack(self.fd.read(self.KEY_SIZE))
            result.append(db)
        return result

    @classmethod
    def add(self, doc_id, comment_num):
        # The data of starting pointer is replaced with id num pair. And
        # increase the starting pointer.
        data = struct.pack('=LL', int(doc_id), int(comment_num))
        lfd = File(None, 'rc', 'r+')
        start_pointer = struct.unpack('=B', lfd.fd.read(self.STARTING_POINTER_SIZE))
        new_start_pointer = struct.pack('=B', start_pointer + 1)
        lfd.fd.seek(0)
        lfd.write(new_start_pointer)

        pointer = start_pointer * self.KEY_SIZE
        lfd.fd.seek(pointer)

        lfd.write(data)
        lfd.close()

    def getAll(self):
        result = []

        for a in range(self.MAX_KEY_NUMBER):
            self.fd.seek(self.start_pointer)

            # The size of struct depends the platform. To use the standard
            # size of types we apply '='.
            keys = self.unpack('=LL', self.fd.read(self.KEY_SIZE))
            result.append(keys)
        return result


    def _unpack(self, data):
        return struct.unpack('=LL', data)

    def setNextPointer(self):
        pass

    def getStartPointer(self):
        data = struct.unpack('=B', self.fd.read(self.STARTING_POINTER_SIZE))
        return data[0]

    def _test_struct_unpack(self):
        fd = file(self.order_db, 'r')
        s_pointer = self.fd.read(self.STARTING_POINTER_SIZE)
        key_num = struct.unpack('=LL', fd.read(self.KEY_SIZE))
        print key_num

    @staticmethod
    def create_test_file():

        init_doc_id = '1110071139'
        init_comment_num = '0'
        #starting_point = struct.pack('=B', RecentComments.STARTING_POINTER_SIZE)
        starting_point = struct.pack('=B', 5)
        
        fd = file(RecentComments.order_db, 'w')
        fd.write(starting_point)
        for a in range(RecentComments.MAX_KEY_NUMBER):
            data = struct.pack('=LL', int(init_doc_id), int(init_comment_num))
            fd.write(data)

            init_doc_id = str(int(init_doc_id) + 1)
            init_comment_num = str(int(init_comment_num) + 1)

        fd.close()


class CommentIndex(object):
    def __init__(self):
        self.init_time = 1317812007.856973
        


class CommentTable(object):
    index_db = 'comment_indicator_db'
    order_db = 'comment_order_db'

    def __init__(self, doc_num, comment_num):
        self.doc_num = doc_num
        self.comment_num = comment_num
        self.fd = file(self.index_db, 'r')
        self.itime = self.fd.read(4)

        time4data = self._ftime2ptime(doc_num)
        self.time = time4data - self.itime

    def gethash(self, key):
        
        pass

    def puthash(self, key, value):
        pass
    

    def _ftime2ptime(self, ftime):
        return time.mktime(time.strptime(ftime, '%y%m%d%H%M'))


    def add(article_comment_num):
        pass
