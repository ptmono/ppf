#!/usr/bin/python
# coding: utf-8

import re, os, time
import config
import libs

import json
import shutil

ERRORP = True
WARNP = True

#Fixme: Why not confg.ERRORP?
def ddError(msg):
    if ERRORP:
        print "ERROR: ", msg

def ddWarnning(msg):
    if WARNP:
        print "WARNNING: ", msg


#TODO: consider the use of FileLock, lockfile
#Fixme: We need more fast way to read file.
#TODO: I don't like class File. I need more simple way. Change entirely.
class File(object):
    """
    The class is used to open a file safely. There is two process AA and
    BB. AA couldn't read the file during BB is writting the _file. AA will
    wait for the time correlated with lock_wait_time and
    lock_wait_interval. The time is lock_wait_time * lock_wait_interval.

    >>> import os.path

    >>> aa = File('1109042210', 'a', 'w')
    >>> aa._backup_filename() #doctest: +ELLIPSIS
    '/.../#1109042210.html#'
    >>> aa._checkBackupFile() #doctest: +SKIP
    >>> aa._checkFile() #doctest: +SKIP

    >>> aa.write('ttuuaa')
    >>> aa.close()

    >>> aa = File('1109042210', 'a', 'r')
    >>> content = aa.read()
    >>> content
    'ttuuaa'
    >>> aa._remove()

    >>> config.htmls_d = config.root_abpath + 'htmlstest/'
    >>> aa = File('1111111112', 'a', 'w')
    >>> aa.write('fjskdf')
    >>> path = aa.filename[:aa.filename.rfind('/')]
    >>> shutil.rmtree(path, ignore_errors=True)


    === Test file lock
    __________________
    >>> doc_id = 1111111111
    >>> file_type = 'a'
    >>> mode = 'w'
    >>> file1 = File(doc_id, file_type, mode)
    >>> #print file1
    >>> file1.write('bbc')
    >>> #os.path.exists(file1._lock_filename())

    ### === Recently comment
    ### __________________________________________________________
    >>> content = "13011103471\\n"
    >>> file2 = File(None, 'rc', 'a+')
    >>> file2.write(content)
    >>> file2.close()

    >>> content = "99011103471\\n"
    >>> file2 = File(None, 'rc', 'a+')
    >>> file2.write(content)
    >>> file2.close()

    >>> file2 = File(None, 'rc', 'r')
    >>> file2.read()
    '13011103471\\n99011103471\\n'

    >>> file2._remove()
    """
    def __init__(self, doc_id, file_type, mode):
        self.doc_id = str(doc_id)
        self.file_type = file_type
        self.mode = mode
        self.filename = self._setFilename(self.doc_id, self.file_type)
        self._lock_filename = self._lock_filename()
        self.lock_wait_count = 0
        self.lock_wait_time = 5
        self.lock_wait_interval = 1
        # We couldn't remove the lock and backup that is created by other
        # object.
        self.permission_lockfile = False
        self.permission_backupfile = False
        self.fd = None
        

    def _setFilename(self, doc_id, file_type):
        if file_type == 'a':
            self.filename = config.article_filename(doc_id)
        elif file_type == 'c':
            self.filename = config.comment_filename(doc_id)
        elif file_type == 'i':
            self.filename = config.index_filename()
        elif file_type == 'rc':
            self.filename = config.recent_comment_filename()
        else:
            raise AttributeError("We require correct mode.")
        return self.filename

    def __call__(self):
        if self.mode == 'w':
            return self.write()
        return self.read()

    def read(self):
        if not self.fd:
            self.fd = self._file()
        return self.fd.read()

    def write(self, content):
        if not self.fd:
            self.fd = self._file()
        self.fd.write(content)
        
    def _file(self):
        try:
            self._waitUnlock()
        except IOError:
            # The server couldn't unlock the file. We can expect there is
            # an accident with file I/O. We restore the file.
            # TODO: Log that. Think more about vulnerability.
            self.restore()
            self._unlockForce()
            self._removeBackupForce()

        if self.mode == 'r':
            self.fd = file(self.filename, self.mode)
            return self.fd
            
        elif self._checkFile():
            self._lock()
            self._backup()

        try:
            fd = file(self.filename, self.mode)
        except IOError:
            dirname = self.filename[:self.filename.rfind('/')]
            os.makedirs(dirname)
            fd = file(self.filename, self.mode)
        return fd

    def close(self):
        # If no self.fd, there is lock file. It means other File object do
        # not complete IO for the document by accident such as blackout.
        # It means we will resore the backup file at later. To prevent the
        # files we use self.permission_lockfile and
        # self.permission_backupfile.
        if (self.mode in ['w', 'w+', 'r+', 'a', 'a+']) and self.permission_lockfile and self.permission_backupfile:
            self._unlockForce()
            self._removeBackupForce()
        self.fd.close()

    def _remove(self):
        "It is not used. Just for test."
        self.close()
        os.remove(self.filename)

    def _checkFile(self):
        return os.path.exists(self.filename)

    def _checkBackupFile(self):
        filep = os.path.exists(self._backup_filename())
        if filep:
            True
        else:
            False

    def _backup_filename(self):
        dirname = os.path.dirname(self.filename)
        filename = os.path.basename(self.filename)
        return dirname + "/#" + filename + "#"
        

    def _backup(self):
        fd = file(self.filename, 'r')
        content = fd.read()
        fd.close()

        # Fixme: Is need error handling?
        fd = file(self._backup_filename(), 'w')
        fd.write(content)
        fd.close()
        self.permission_backupfile = True

    def _removeBackupForce(self):
        try:
            os.remove(self._backup_filename())
        except OSError:
            # No such file or directory
            pass

    def restore(self):
        filename = self._backup_filename()
        fd = file(filename, 'r')
        content = fd.read()
        fd.close()

        fd = file(filename, 'w')
        fd.write(content)
        fd.close()
        
    def _lock_filename(self):
        
        result = self.filename + ".lock"
        return result

    def _checkLockp(self):
        return os.path.exists(self._lock_filename)

    def _lock(self):
        "Lock the file"
        self._waitUnlock()
        fd = file(self._lock_filename, 'w')
        fd.close()
        self.permission_lockfile = True

    def _unlockForce(self):
        try:
            os.remove(self._lock_filename)
        except OSError:
            # No such file or directory
            pass

    def _waitUnlock(self):
        """
        Couldn't unlock the function returns IOError.
        """
        if self._checkLockp():
            while (self.lock_wait_count < self.lock_wait_time):
                time.sleep(self.lock_wait_interval)
                if not self._checkLockp():
                    return True
                self.lock_wait_count += 1
            raise IOError("Already exists lock file %s" % self._lock_filename)






class Tools(object):

    def _file(self, filename, mode):
        """For file locking. We maybe need a tool to open a file with 'w'
        mode. To prevent a crash.
        """
        
        return file(filename, mode)

    def _close(self, fd):
        return fd.close()




#TODO: 9 consider the use of collections.OrderedDict
class InfoTemplate(dict):
    """
    >>> json = {'date': 1108252154, 'name': 'dalsoo', 'password': '3232', 'email':'pp@naver.com','content':'cccc'}
    >>> aa = InfoTemplate()
    >>> aa.setFromDict(json)
    >>> aa
    {'date': 1108252154, 'content': 'cccc', 'password': '3232', 'name': 'dalsoo', 'email': 'pp@naver.com'}
    >>> aa.name
    'dalsoo'
    >>> aa.name = 'Talsu'
    >>> aa
    {'date': 1108252154, 'content': 'cccc', 'password': '3232', 'name': 'Talsu', 'email': 'pp@naver.com'}

    >>> aa['content']
    'cccc'

    >>> aa['content'] = 'dddd'
    >>> aa.content
    'dddd'

    >>> aa.updateFromDict({})

    >>> aa.setFromDict({})
    >>> aa
    {'date': '', 'content': '', 'password': '', 'name': '', 'email': ''}

    """
    info = ['date', 'name', 'password', 'email', 'content']

    def __init__(self):
        self.init()

    def init(self):
        for key in self.info:
            setattr(self, key, '')

    def __repr__(self):
        return repr(self.__dict__)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def updateFromDict(self, value):
        keys = self.__dict__.keys()
        for key in value:
            if key in keys:
                self.__dict__[key] = value[key]

    def setFromDict(self, value):
        self.init()
        self.updateFromDict(value)
    

class InfosTemplate(object):
    """
    >>> #from indexer import InfosTemplate, InfoTemplate
    >>> json = {'1':{'date': 1108252154, 'name': 'dalsoo', 'password': '3232', 'email':'pp@naver.com','content':'cccc'}, '2':{'date': 1108252155, 'name': 'dalsoo', 'password': '3232', 'email':'pp@naver.com','content':'cccc2'}, '3':{'date': 1108252156, 'name': 'dalsoo', 'password': '3232', 'email':'pp@naver.com','content':'cccc3'}}
    >>> json_bb = {'8': {'date': 1108252159, 'name': 'hosoo', 'password': '3232', 'email':'pp@naver.com','content':'cccc4'}}

    >>> aa_obj, bb_obj = None, None
    >>> def init_obj():
    ...  global aa_obj, bb_obj
    ...  aa_obj = InfosTemplate()
    ...  aa_obj.setFromDict(json)
    ...  bb_obj = InfosTemplate()
    ...  bb_obj.setFromDict(json_bb)
    ...

    >>> ### test basic methods
    >>> init_obj()
    >>> aa_obj.isinstance(bb_obj)
    True
    >>> aa_obj.isinstance(int) #doctest: +IGNORE_EXCEPTION_DETAIL 
    Traceback (most recent call last):
    TypeError: InfosTemplate type is required


    === Test object iteration
    _________________________
    >>> aa = InfosTemplate()
    >>> aa.infoObj = InfoTemplate
    >>> aa.setFromDict({})
    >>> aa.setFromDict(json)
    >>> aa
    {'1': {'date': 1108252154, 'content': 'cccc', 'password': '3232', 'name': 'dalsoo', 'email': 'pp@naver.com'}, '3': {'date': 1108252156, 'content': 'cccc3', 'password': '3232', 'name': 'dalsoo', 'email': 'pp@naver.com'}, '2': {'date': 1108252155, 'content': 'cccc2', 'password': '3232', 'name': 'dalsoo', 'email': 'pp@naver.com'}}
    >>> aa.indexes
    ['1', '2', '3']
    >>> len(aa)
    3
    
    >>> for a in aa:
    ...  print a.date
    ...  
    1108252156
    1108252155
    1108252154

    >>> a = aa['1']
    >>> a
    {'date': 1108252154, 'content': 'cccc', 'password': '3232', 'name': 'dalsoo', 'email': 'pp@naver.com'}
    >>> a.date
    1108252154


    === Test object append method
    _____________________________
    >>> appended_json = {'4':{'date': 1108252157, 'name': 'dalsoo', 'password': '3232', 'email':'pp@naver.com','content':'cccc4'}}
    >>> aa.update(appended_json)
    >>> aa['4']
    {'date': 1108252157, 'content': 'cccc4', 'password': '3232', 'name': 'dalsoo', 'email': 'pp@naver.com'}
    >>> init_obj()
    >>> cc_obj = aa_obj + bb_obj
    >>> cc_obj
    {'1': {'date': 1108252154, 'content': 'cccc', 'password': '3232', 'name': 'dalsoo', 'email': 'pp@naver.com'}, '8': {'date': 1108252159, 'content': 'cccc4', 'password': '3232', 'name': 'hosoo', 'email': 'pp@naver.com'}, '3': {'date': 1108252156, 'content': 'cccc3', 'password': '3232', 'name': 'dalsoo', 'email': 'pp@naver.com'}, '2': {'date': 1108252155, 'content': 'cccc2', 'password': '3232', 'name': 'dalsoo', 'email': 'pp@naver.com'}, '4': {'date': 1108252157, 'content': 'cccc4', 'password': '3232', 'name': 'dalsoo', 'email': 'pp@naver.com'}}


    === Test error handling
    _______________________
    >>> aa[1] #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    KeyError: 1

    >>> aa.indexes
    ['1', '2', '3', '4']

    >>> vk = {'10': {'date': '', 'content': '', 'password': '3232', 'name': 'dalsoo', 'email': 'pp@naver.com'}}
    >>> aa.update(vk)

    """
    infoObj = InfoTemplate

    def __init__(self):
        self.json = {}
        self.indexes = []

    def save(self):
        pass

    def set(self):
        pass

    def setFromDict(self, value):
        self.json = value
        self.refresh()

    def next(self):
        if not self.indexes:
            self.refresh()
            raise StopIteration

        key = self.indexes.pop()
        value = self.json[key]
        info = self.infoObj()
        info.setFromDict(value)
        return info

    def __iter__(self):
        return self

    def __repr__(self):
        return repr(self.json)

    def refresh(self):
        self.indexes = sorted(self.json, key=lambda a: int(a))

    def __getitem__(self, key):
        value = self.json[key]
        obj = self.infoObj()
        obj.setFromDict(value)
        return obj

    def __setitem__(self, key, value):
        self.json[key] = value
        self.refresh()

    def __len__(self):
        return len(self.json)

    def _checkStringp(self, s):
        if isinstance(s, str):
            return True
        return False

    def update(self, value_dict):
        "Add or update our dict from dict. It similar dict.update."
        for key in value_dict:
            self.json[key] = value_dict[key]
        self.refresh()


    def __add__(self, other):
        self.isinstance(other)

        result = self.__class__()
        result.setFromDict(self.json)
        result.update(other.json)
        return result

    @classmethod
    def isinstance(self, other):
        if isinstance(other, self):
            return True
        raise TypeError("%s type is required" % self.__name__)



class Comment(InfoTemplate):
    info = ['comment_id', 'date', 'name', 'password', 'email', 'content']

#DONE: add delete method
class Comments(InfosTemplate):
    """
    The article can contains the comments. The article can indicated by
    the id of the document. We can get the comments of the article with the id of the article.

    comments = Comments(doc_id)
    Or
    comments = Comments()
    comments.set(doc_id)

    doc_id is the id of the article. doc_id is used to determine the
    database filename which contains the data of comments of the article.


    >>> json = {'1': {'date': '11/08/31', 'name': 'Talsu', 'password': 'a', 'content': '이건 이런 있을 수 없는 일 잉 있나 오옹오오 그러 나 하지만 업수로 아작'}, '2': {'date': '11/09/31', 'name': 'Tal', 'password': 'a', 'content': '이건 이런 있을 수 없는 일 잉 있나 오옹오오 그러 나 하지만 업수로 아작'}, '3': {'date': '11/09/20', 'name': 'dalsoo', 'password': 'a', 'content': '그러 나 하지만 업수로 아작'}}


    >>> comments = Comments()
    >>> comments.set("1108261752") #doctest: +SKIP

    >>> #comments.set("0706012057")
    >>> comments.setFromDict(json)
    >>> print comments['1'].content
    이건 이런 있을 수 없는 일 잉 있나 오옹오오 그러 나 하지만 업수로 아작


    === Test updating. updateFromObj
    ________________________________
    >>> comment = Comment()
    >>> comment.name = "Talsu"
    >>> comment.content = "This is the content of comment"

    # Comment object requires doc_id
    >>> comments.updateFromObj(comment) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    AttributeError: The object requires attribute doc_id
    >>> comments.doc_id = '0706012057'
    >>> comments.updateFromObj(comment)
    >>> comments['4']
    {'name': 'Talsu', 'comment_id': '4', 'content': 'This is the content of comment', 'date': '', 'password': '', 'email': ''}


    === Test indexing
    _________________
    >>> comments.indexes
    ['4', '3', '2', '1']

    >>> ### Test new comment
    >>> # There is no exist comment for doc_id
    >>> #new_comments = Comments('0205241422')
    >>> #new_comments.json
    >>> #{}
    >>> #new_comments.updateFromObj(comment)

    === Test count
    --------------
    >>> comments.counts()
    4


    === Test delete/update static method
    ____________________________________
    >>> Comments.delete('0706012057', '8')
    >>> Comments.delete('0706012057', '8') #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    KeyError: "We has the key '8'"

    >>> Comments.update('0706012057', '8', comment)
    >>> comments = Comments('0706012057')



    """
    infoObj = Comment

    def __init__(self, doc_id=''):
        super(Comments, self).__init__()
        self.doc_id = doc_id
        if self.doc_id:
            self.set(self.doc_id)

    def set(self, doc_id):
        # Load json
        self.doc_id = str(doc_id)
        try:
            fd = File(self.doc_id, 'c', 'r')
            content = fd.read()
            fd.close()
        except IOError:
            # There is no comment file.
            content = '{}'
        try:
            json_load = json.loads(content)
        except ValueError:
            # We get empty content.
            json_load = {}

        # Set json
        self.setFromDict(json_load)

    def save(self):
        json_dump = json.dumps(self.json)
        fd = File(self.doc_id, 'c', 'w')
        fd.write(json_dump)
        fd.close()

    def filename(self):
        self.checkDocId()
        return config.comments_d + self.doc_id + config.comment_extension

    def counts(self):
        return len(self)

    def updateFromObj(self, comment_obj):
        """
        We can use to add a comment from comment object.
        
        """
        self.checkDocId()
        key = self.newIndex()
        # Add comment id
        comment_obj.comment_id = key
        value = comment_obj.__dict__
        self.json[key] = value
        self.refresh()

    def checkDocId(self):
        if not self.doc_id:
            raise AttributeError, "The object requires attribute doc_id"

    def refresh(self):
        self.indexes = sorted(self.json, key=lambda a: int(a), reverse=True)

    def newIndex(self):
        if self.indexes:
            result = int(self.indexes[0]) + 1
            return str(result)
        else:
            # There is no index. We start the index from 1.
            return '1'

    @staticmethod
    def delete(doc_id, key):
        "It is used to delete a comment for the document id."
        comments = Comments()
        comments.set(doc_id)
        try:
            comments.json.pop(key)
        except KeyError, err:
            raise KeyError("We has no key %s" % err)
        comments.save()

    @staticmethod
    def update(doc_id, key, obj):
        "It is used to modify a comment for the document id."
        comments = Comments()
        comments.set(doc_id)
        comments.json[key] = obj.__dict__
        comments.save()
        
        


class Article(InfoTemplate):
    """
    
    >>> # get new article
    >>> aObj = Article()
    >>> aObj.set(1201191546)
    >>> aObj.setFromId("akkk")
    WARNNING:  AttributeError("'NoneType' object has no attribute 'group'",)
    We couldn't fine key and value in the document. doc_id is akkk
    >>> aObj.setFromId("0705241422") #doctest: +SKIP
    >>> aObj.__dict__ #doctest: +SKIP
    {'category': '', 'author': 'this is author', 'unpublished': '', 'title': 'This is sixth title', 'update': '1108170952', 'tag': 'python', 'date': '1108170951', 'doc_id': '0705241422'}

    >>> article = Article()
    >>> article.setFromId('9999999999') #doctest: +SKIP
    """
    info = config.article_informations

    def __init__(self, doc_id=''):
        super(Article, self).__init__()
        self.doc_id = str(doc_id)

    def _getMuse(self):
        """
        Get the content of muse file.
        """
        #Todo: Is it need error handling for self.doc_id ?
        filename = self._path(self.doc_id)
        try:
            fd = file(filename, 'r')
            content = fd.read()
        except:
            content = ''
        return content

    @classmethod
    def writeHtml(self, doc_id, content):
        "Set the content of article. The file is html."
        try:
            fd = File(str(doc_id), 'a', 'w')
            fd.write(content)
            fd.close()
        except:
            msg = "We couldn't write %s" % doc_id
            libs.logError(msg)

    def set(self, doc_id):
        "The object have to contains the id of document to be used with Articles."
        self.doc_id = str(doc_id)

    def setFromId(self, doc_id):
        """
        Set the object from the id of the muse document. From this method
        we can set the object from file directly.

        """
        self.doc_id = str(doc_id)
        json_dict = self._getInfoTableFromFileAsDict(self.doc_id)
        self.updateFromDict(json_dict)

    def _getInfoTableFromFileAsDict(self, doc_id):
        doc_id = str(doc_id)
        result = {}
        key_and_value_regexp = "^#([^ ]+) (.*)"
        # Our tags start point-min to \n\n. We get the content of tags.
        # Then we will separate the tag and value.
        content = self._getInfoTableFromFileAsString(doc_id)
        content_l = content.split('\n')
        regexobj = re.compile(key_and_value_regexp)

        for el in content_l:
            try:
                matchobj = regexobj.match(el)
                key = matchobj.group(1)
                value = matchobj.group(2)
            except AttributeError, err:
                # There is no key and value in article
                ddWarnning(repr(err) + "\n" + \
                               "We couldn't fine key and value in the document. doc_id is " + \
                               doc_id)
                continue
            result[key] = value

        return result

    def _getInfoTableFromFileAsString(self, doc_id):
        filename = self._path(doc_id)
        end_of_info_regexp = "\n\n"

        try:
            fd = file(filename, 'r')
            content = fd.read()
        except IOError:
            # There is no article
            content = ''

        end_of_info_pos = self._getMatchPosition(end_of_info_regexp, content)
        return content[:end_of_info_pos]

    def _path(self, doc_id):
        result = ''
        if not doc_id:
            result = None
        else:
            result = os.path.join(config.muses_d, doc_id + config.muse_extension)
        return result

    def _getMatchPosition(self, regexp, text):
        try:
            ab = re.search(regexp, text)
            point_to_be_match = ab.start()
        except:
            point_to_be_match = 0
        return point_to_be_match


class Articles(InfosTemplate):
    """

    >>> json_dict = {'0702052011': {'category': 'emacs planner', 'date': '1108170951', 'author': 'this is author', 'update': '1108170952', 'title': 'Title'}, '0702052099': {'category': 'python', 'date': '1108170951', 'author': 'this is author', 'update': '1108170952', 'title': 'This is title 2'}, '0702052033': {'category': 'python', 'date': '1108170951', 'author': 'this is author', 'update': '1108170952', 'title': 'This is title 3'}}

    >>> articles = Articles()
    >>> articles.set() #doctest: +SKIP
    >>> articles.setFromDict(json_dict)

    >>> #articles['0702052011']
    >>> #returns value for key. not object

    >>> # to returns object
    >>> article = articles.article('0702052011')
    >>> article.title
    'Title'

    >>> print articles.article('111111')
    None

    >>> article = Article()
    >>> article.name = "Talsu"
    >>> article.content = "This is content"
    >>> articles.updateFromObj(article) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    AttributeError: Object requires a attribute doc_id
    >>> articles.json
    {'0702052011': {'category': 'emacs planner', 'date': '1108170951', 'title': 'Title', 'update': '1108170952', 'author': 'this is author'}, '0702052033': {'category': 'python', 'date': '1108170951', 'title': 'This is title 3', 'update': '1108170952', 'author': 'this is author'}, '0702052099': {'category': 'python', 'date': '1108170951', 'title': 'This is title 2', 'update': '1108170952', 'author': 'this is author'}}

    >>> len_json = len(articles.json)
    >>> u_dict = {'0702052011' : {'category': 'emacs planner', 'date': '1108170951', 'title': 'Title', 'update': '1108170952', 'author': 'this is author'}}
    >>> articles.update(u_dict)
    >>> assert len(articles.json) == len_json

    >>> u_dict = {'9999999999' : {'category': 'emacs planner', 'date': '1108170951', 'title': 'Title', 'update': '1108170952', 'author': 'this is author'}}
    >>> articles.update(u_dict)
    >>> assert len(articles.json) == len_json + 1

    """
    infoObj = Article
    db_filename = config.index_filename()

    def next(self):
        if not self.indexes:
            self.refresh()
            raise StopIteration

        key = self.indexes.pop()
        value = self.json[key]
        value['doc_id'] = key
        comment = self.infoObj()
        comment.setFromDict(value)
        return comment

    def set(self):
        fd = file(self.db_filename, 'r')
        content = fd.read()
        try:
            json_load = json.loads(content)
        except ValueError:
            json_load = {}

        self.setFromDict(json_load)

    def save(self):
        json_dump = json.dumps(self.json)
        fd = File('', 'i', 'w')
        fd.write(json_dump)
        fd.close()

    def article(self, doc_num):
        """
        Returns articles object with the document number. DOC_NUM is the
        docmunt number as string.
        """

        # When no doc_num in self.json ?
        try:
            json_dict = self.json[doc_num]
        except KeyError:
            return None

        result = self.infoObj()
        result.doc_id = doc_num
        result.setFromDict(json_dict)
        return result

    def updateFromObj(self, obj):
        if not obj.doc_id:
            raise AttributeError("Object requires a attribute doc_id")
        key = obj.doc_id
        value = obj.__dict__
        self.json[key] = value
        self.refresh()

        


class Index(Tools):
    """
    

    >>> aa = Index()
    >>> aa._create() #doctest: +SKIP
    """
    filename = config.index_filename()

    def create(self):
        json_dict = self._create()
        json_dump = json.dumps(json_dict)
        fd = self._file(self.filename, 'w')
        fd.write(json_dump)
        fd.close()


    def _create(self):
        result = {}
        file_l = os.listdir(config.muses_d)

        article = Article()
        for f in file_l:
            if self._museExtensionp(f):
                doc_id = self._getDocNumFromFilename(f)
                article.setFromId(doc_id)
                result[doc_id] = article.__dict__
            else:
                continue
        return result

    def _museExtensionp(self, filename):
        "Is it has the muse extension?"
        ext_length = len(config.muse_extension)
        if filename[-ext_length:] == config.muse_extension:
            return True
        else:
            return False

    def _getDocNumFromFilename(self, filename):
        ext_length = len(config.muse_extension)
        return filename[:-ext_length]



class CommentBasic(object):
    info = ['date', 'name', 'password', 'email', 'content']
    separator = "aknd4#\n"

    def __init__(self):
        self.create_local_variables()

    def __repr__(self):
        return repr(self.__dict__)

    def create_local_variables(self):
        for name in self.file_info:
            setattr(self, name, '')


#Obsolete
class CommentsL(object):
    """

    >>> json = [{'1':{'date': 1108252154, 'name': 'dalsoo', 'password': '3232', 'email':'pp@naver.com','content':'cccc'}}, {'2':{'date': 1108252155, 'name': 'dalsoo', 'password': '3232', 'email':'pp@naver.com','content':'cccc2'}}, {'3':{'date': 1108252156, 'name': 'dalsoo', 'password': '3232', 'email':'pp@naver.com','content':'cccc3'}}]

    >>> ### test object iteration
    >>> aa = CommentsL()
    >>> aa.setFromJson(json)
    >>> for a in aa:
    ...  print a.date
    ...
    1108252156
    1108252155
    1108252154
    >>> aa[1].date
    1108252155

    >>> ### test object set
    >>> #Fixme: set the object
    >>> #Todo: We need this behavier?
    >>> aa[1].date = 1108252160
    >>> aa[1].date #doctest: +SKIP
    1108252160
    >>> ## Set item
    >>> aa[1] = {'2':{'date': 1108252155, 'name': 'dddd', 'password': '3232', 'email':'pp@naver.com','content':'cccc2'}}
    >>> aa[1].name
    'dddd'

    >>> ### test object append method
    >>> # To update comments for an article we can use InfosTemplate class.
    >>> appended_json = {'4':{'date': 1108252157, 'name': 'dalsoo', 'password': '3232', 'email':'pp@naver.com','content':'cccc4'}}
    >>> aa.append(appended_json) #doctest: +SKIP
    """
    def __init__(self, doc_num=None, mode='r'):
        self.json = []
        self.idx = 0
        self.length = 0
        
    def next(self):
        if self.idx >= self.length:
            self.refresh()
            raise StopIteration

        json_dict = self.__getJsonForComment(self.idx)
        result = InfoTemplate()
        result.setFromDict(json_dict)
        self.idx += 1
        return result

    def __iter__(self):
        return self
        
    def refresh(self):
        self.idx = 0

    def __getitem__(self, key):
        json_dict = self.__getJsonForComment(key)
        obj = InfoTemplate()
        obj.setFromDict(json_dict)
        return obj

    def __setitem__(self, key, value):
        self.json[key] = value

    def append(self, json):
        # Todo: do?
        # key = json.keys()[0]
        # print key
        # value = json[key]
        # print value
        # self.json[key] = value
        pass

    def __getJsonForComment(self, idx):
        """
        index of self.json provides
        {'1':{'date': 1108252154, 'name': 'dalsoo', 'password': '3232', 'email':'pp@naver.com','content':'cccc'}}
        InfoTemplate class uses only
        {'date': 1108252154, 'name': 'dalsoo', 'password': '3232', 'email':'pp@naver.com','content':'cccc'}
        """
        json_dict = self.json[idx]
        result = json_dict.values()[0]
        return result

    def set(self, doc_num):
        ab_filename = config.comments_d + self.doc_num + config.comment_extension
        fd = file(ab_filename, 'r')
        # [{'date': 1108252154, 'name': 'dalsoo', 'password': '3232', 'email':'pp@naver.com','content':'cccc'}, {'date': 1108252155, 'name2': 'dalsoo', 'password': '3232', 'email':'pp@naver.com','contnet':'cccc2'}]
        content = fd.read()
        fd.close()
        json_load = json.loads(content)
        self.json = json_load

    def setFromJson(self, json_dict):
        self.json = sorted(json_dict, reverse=True)
        self.length = len(self.json)

