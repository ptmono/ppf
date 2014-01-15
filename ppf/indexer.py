#!/usr/bin/python
# coding: utf-8

from __future__ import unicode_literals
import re, os, time
import json
import shutil

from io import open

from dlibs.d_os import File
from dlibs.logger import loggero

from . import config
from . import libs

try:
    unicode
except:
    unicode = str


ERRORP = True
WARNP = True

#Fixme: Why not confg.ERRORP?
def ddError(msg):
    if ERRORP:
        print("ERROR: ", msg)

def ddWarnning(msg):
    if WARNP:
        print("WARNNING: ", msg)


#TODO: Consider use use of FileLock, lockfile
#Fixme: We need more fast way to read file.
#TODO: I don't like This class. I need more simple way. Change entirely.
class File(File):
    def __init__(self, doc_id, file_type, mode, lock_interval=1):
        filename = self._setFilename(str(doc_id), file_type)
        super(File, self).__init__(filename, mode, lock_interval)
        
    def _setFilename(self, doc_id, file_type):
        if file_type in ['a', 'article']:
            self.filename = config.article_filename(doc_id)
        elif file_type in ['c', 'comment']:
            self.filename =config.comment_filename(doc_id)
        elif file_type in ['i', 'index']:
            self.filename = config.index_filename()
        elif file_type in ['rc', 'recent_comment']:
            self.filename = config.recent_comment_filename()
        else:
            raise AttributeError("We require correct mode.")
        return self.filename
    

class Tools(object):

    def _file(self, filename, mode):
        """For file locking. We maybe need a tool to open a file with 'w'
        mode. To prevent a crash.
        """
        
        return open(filename, mode)

    def _close(self, fd):
        return fd.close()


#TODO: 9 consider the use of collections.OrderedDict
class InfoTemplate(dict):
    """
    """
    info = ['date', 'name', 'password', 'email', 'content']

    def __init__(self):
        self.init()

    def init(self):
        super(InfoTemplate, self).__init__()
        for key in self.info:
            setattr(self, key, '')

    def __repr__(self):
        return repr(self.__dict__)

    def __eq__(self, other):
        if isinstance(other, dict):
            return self.__dict__ == other
        return False

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
    """
    infoObj = InfoTemplate

    def __init__(self):
        self.json = {}
        self.indexes = []

    def save(self):
        pass

    def set(self):
        pass

    def __eq__(self, other):
        if isinstance(other, dict):
            return self.json == other
        elif isinstance(other, self.__class__):
            return self.json == other.json
        return False

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

    def __next__(self):
        return self.next()

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
            raise AttributeError("The object requires attribute doc_id")

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
        except KeyError as err:
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
            fd = open(filename, 'r')
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
        except Exception as err:
            msg = "We couldn't write %s" % doc_id
            loggero().error(msg)
            loggero().error(err)
            raise Exception(err)

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
            except AttributeError as err:
                # There is no key and value in article
                msg = repr(err) + "\nWe couldn't fine key and value in the document. doc_id is " + doc_id
                loggero().warning(msg)
                continue
            result[key] = value

        return result

    def _getInfoTableFromFileAsString(self, doc_id):
        filename = self._path(doc_id)
        end_of_info_regexp = "\n\n"

        try:
            fd = open(filename, 'r')
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
        try:
            fd = open(self.db_filename, 'r')
            content = fd.read()
            json_load = json.loads(content)
        except (ValueError, IOError, OSError):
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

    def is_article(self, doc_num):
        return self.article(doc_num)

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


