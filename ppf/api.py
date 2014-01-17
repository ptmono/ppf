#!/usr/bin/python
# coding: utf-8

"""
Write a function like deleteComment/updateArticle/updateIndex to add new
api. The function uses the arguments posted by the client as the string
query. 

The client can create a query string.

'cmd' field is the name of function. The arguments of the function are
other fields. A query string to delete a comment of a article is created
by

data = Data()
data.doc_id = '1109091702'
data.comment_id = '6'
data.urlencode()

We have to encode the query if the query contains Unicode query, python
dictionary or list. In server we have to decode the query. Conveniently
decode and encode the query we can use the underbar argument. The argument
of the api that start the underbar('_') has special mean. To create a
query string we can use Data class. The Data can detect automatically the
underbar argument of the api function.

Let's create an api instead to explain the underbar argument. To update
the index, we need a function

def updateIndex(doc_id, _jsonbase64_dict):
    "Used to add/modify the table of articles."
    article = Article(doc_id)
    article.updateFromDict(_jsonbase64_dict)
    articles = Articles()
    articles.updateFromObj(article)
    articles.save()

where the article object requries doc_id to be used with the articles
object.

_jsonbase64_dict is a python dictionary like

{'0702052011': {'category': 'emacs planner', 'date': '1108170951', 'title': 'Title', 'update': '1108170952', 'author': 'this is author'}, '0702052033': {'category': 'python', 'date': '1108170951', 'title': 'This is title 3', 'update': '1108170952', 'author': 'this is cjk 한글'}}

We encode the dictionary base64.b64encode(json.dumps(s)) where s is the
dictionary. We decode that with json.loads(base64.b64decode(s)).

Let's specify the encoding/decoding within Data class.

class Data(DataBasic):
    prefix_list = ['base64', 'jsonBase64']
    function_prefix_of_encode = "encode_"
    function_prefix_of_decode = "decode_"

    @classmethod
    def encode_jsonBase64(self, s):
        return base64.b64encode(json.dumps(s))

    @classmethod
    def decode_jsonBase64(self, s):
        return json.loads(base64.b64decode(s))

Then we can encode the query.

data = DataBasic()
data._jsonbase64_dict = s
data.urlencode()

"""
from __future__ import unicode_literals
import sys
import os
import time
import cgi

import base64
import json
import hmac
import inspect

from . import config
from . import libs
from .indexer import Article, Articles, Comments, Comment
from . import html_messages as hm

from dlibs.structures.dict import DictTypeAMixIn
from dlibs.logger import loggero

#if config.LOCAL_TEST:
import cgitb
cgitb.enable()

from flask import request, abort



try:
    from urllib import urlencode
except:
    from urllib.parse import urlencode


class Key(object):

    def __init__(self, msg):
        self.msg = self._ourMsg(msg)

    def create(self):
        o = hmac.new(config.key, self.msg)
        return o.hexdigest()
    
    def check(self, key):
        our_key = self.create()
        if key is our_key:
            return True
        else:
            return False

    def _ourMsg(self, msg):
        return msg[:100]

    
class DataBasic(DictTypeAMixIn):
    """
    The class creates the query string. The field and value is assigned.

    The class is related to the api module. The api module has the
    functions. Each function has arguments. If the argument has "base64_"
    _prefix, then self.encode function will encode the data with the
    base64 encoder.

    """
    prefix_list = []
    function_prefix_of_encode = ''
    function_prefix_of_decode = ''

    def __repr__(self):
        return repr(self.__dict__)

    def pop(self, key):
        self.__dict__.pop(key)

    def urlencode(self):
        "Return the encoded string query."
        origin = self.__dict__
        data = self.__encode(self.__dict__)
        result = urlencode(self.__dict__)
        self.__dict__ = origin
        return result

    def __encode(self, data):
        for key in self.__dict__:
            prefix = self._prefix(key)
            if prefix in self.prefix_list:
                encoder = getattr(self, self.function_prefix_of_encode + prefix)
                value = self.__dict__[key]
                self.__dict__[key] = encoder(value)

    def __decode(self):
        for key in self.__dict__:
            prefix = self._prefix(key)
            if prefix in self.prefix_list:
                decoder = getattr(self, self.function_prefix_of_decode + prefix)
                value = self.__dict__[key]
                self.__dict__[key] = decoder(value)

    @classmethod
    def _prefix(self, key):
        """
        Find the prefix of the key. The prefix start underbar and end
        underbar.
        """
        if not self.hasPrefix(key):
            return False
        start_point = 1
        end_point = key.find('_', start_point)
        return key[start_point:end_point]

    @classmethod
    def hasPrefix(self, key):
        check_prefix = key.find('_')
        if not check_prefix == 0:
            return False
        prefix_start_point = 1
        check_prefix_end = key.find('_', prefix_start_point)
        if check_prefix_end == -1 or len(key) == check_prefix_end +1:
            return False
        return True

    @classmethod
    def toByte(self, value):

        try:
            return value.encode('utf-8')
        except(UnicodeDecodeError, AttributeError):
            raise Exception("The data value must be unicode not bytes.")

    @classmethod
    def toUnicode(self, value):
        return value.decode('utf-8')
            

# We use only the text(unicode) string. base64 uses the byte string. json
# uses text(unicode) string.
class Data(DataBasic):
    prefix_list = ['base64', 'jsonBase64']
    function_prefix_of_encode = "encode_"
    function_prefix_of_decode = "decode_"

    @classmethod
    def encode_base64(self, s):
        """ s will be always unicode.
        Return byte.
        """
        s = self.toByte(s)
        return base64.b64encode(s)

    @classmethod
    def decode_base64(self, s):
        """ s always pass encode_base64. So the type of s is byte.
        Return text(unicode).
        """
        result = base64.b64decode(s)
        result = self.toUnicode(result)
        return result

    @classmethod
    def encode_jsonBase64(self, s):
        """ s will be always unicode.
        Return byte.
        """
        s = json.dumps(s)
        s = self.toByte(s)
        return base64.b64encode(s)

    @classmethod
    def decode_jsonBase64(self, s):
        """ s always pass encode_jsonBase64. So the type of s is byte.
        Return text(unicode).
        """
        result = base64.b64decode(s) # byte
        # json requires unicode
        result = self.toUnicode(result)
        result = json.loads(result)
        return result

    def decode_value(self, key, value):
        result = None
        prefix = self._prefix(key)
        if prefix:
            decoder = getattr(self, self.function_prefix_of_decode + prefix)
            result = decoder(value)
        return result

def getComments(doc_id):
    comments = Comments(doc_id)
    return str(comments)
    
def deleteComment(doc_id, comment_id):
    "Delete comment for an article."
    try:
        Comments.delete(doc_id, comment_id)
        return u'ok'
    except:
        abort(500)

def writeComment(doc_id, _base64_content, _base64_name='', password=''):

    articles = Articles()
    if not articles.is_article(doc_id):
        loggero().info(doc_id)
        
        abort(500)
    
    try:    
        comment = Comment()
        comment.date = time.strftime("%m/%d|%y", time.localtime())
        comment.name = _base64_name
        # TODO: How to prevent password??
        comment.password = password
        comment.content = _base64_content
        comments = Comments(doc_id)
        comments.updateFromObj(comment)
        comments.save()
        return u'ok'
    except:
        abort(500)

def writeArticle(doc_id, _base64_content):
    "Used to create/modify the content of an article."

    article = Article()
    article.writeHtml(doc_id, _base64_content)

    return u'ok'

def updateIndex(doc_id, _jsonBase64_dict):
    "Used to add/modify the table of articles."
    article = Article()
    # Article have to contains doc_id to be used with Articles.
    article.set(doc_id)
    article.updateFromDict(_jsonBase64_dict)
    articles = Articles()
    articles.set()
    articles.updateFromObj(article)
    articles.save()

    loggero().info('aaaac')

    return u'ok'

    print("Content-type: text/html\n\n")
    print("OK")

def updateFile(filename, _base64_content):
    abpath = config.files_d + filename
    if os.path.exists(abpath):
        print("Content-type: text/html\n\n")
        print("False")
        return
    fd = file(abpath, 'w')
    fd.write(_base64_content)
    fd.close()

    return u'ok'
    print("Content-type: text/html\n\n")
    print("OK")


def updateServerFile(filename, _base64_content):
    "Update the server file."
    libs.lock()
    abpath = config.root_abpath + filename
    fd = file(abpath, 'w')
    fd.write(_base64_content)
    fd.close()
    libs.unlock()


def checkSecureKey(secure_key):
    # TODO: Why not "is" instead of "==".
    if secure_key == config.SECURE_KEY:
        return True
    return False


### For testing
def articles_length():
    articles = Articles()
    articles.set()
    length = len(articles)
    hm.print_msg(str(length))

def comments_length(doc_id):
    comments = Comments()
    comments.set(doc_id)
    length = len(comments)
    hm.print_msg(str(length))

def article_json(doc_id):
    articles = Articles()
    articles.set()
    article = articles.article(doc_id)
    # To use in client we have to dumps with json
    hm.print_msg(json.dumps(article.__dict__))

def main():

    form = cgi.FieldStorage()
    try: secure_key = form['secure_key'].value
    except: return u"denied"
    if not checkSecureKey(secure_key): return u"denied"

    if form.has_key('cmd'):
        data = Data()
        values = []
        scmd = form['cmd'].value
        # Get comment object
        try: cmd = eval(scmd)
        except: return

        # Get the arguments of function
        spec = inspect.getargspec(cmd)
        #try:
        for arg in spec.args:
            value = form[arg].value
            # Encode
            if data.hasPrefix(arg): value = data.decode_value(arg, value)
            values.append(value)
        apply(cmd, values)
        #except:
        #    sys.exit(1)
    # print("Content-type: text/html\n")
    # print("test")
    return


class _Executor(object):

    def __init__(self, request):
        self.form = request.form

    def is_validate(self, form):
        try: secure_key = form['secure_key']
        except: return False

        if not checkSecureKey(secure_key):
            return False

        try:
            self.cmd = form['cmd']
            self.cmd = eval(self.cmd)
        except:
            return False
        return True

    def execute(self):
        if not self.is_validate(self.form):
            return u'denied1'

        # Get the arguments of function
        spec = inspect.getargspec(self.cmd)
        data = Data()
        values = []

        for arg in spec.args:
            try:
                value = self.form[arg]
            except: return u'denied2'

            if data.hasPrefix(arg): value = data.decode_value(arg, value)
            values.append(value)

        try:
            result = self.cmd(*values)
        except IOError as err:
            config.logger.error(str(err))
            return u'denied3'

        return result
            
        
        
        

def main_wsgi(request):

    manager = _Executor(request)
    return manager.execute()
    
if __name__ == "__main__":
    main()
