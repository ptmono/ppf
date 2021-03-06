#!/usr/bin/python
# coding: utf-8

import os, sys
import re

try:
    from urllib2 import urlopen, Request
except:
    from urllib.request import urlopen, Request
    unicode = str
import hmac
import inspect
import json

__current_abpath = os.path.realpath(os.path.dirname(__file__)) + "/"
root_abpath = os.path.dirname(os.path.dirname(os.path.dirname(__current_abpath)))

if root_abpath not in sys.path:
    sys.path.insert(0, root_abpath)


from dlibs.logger import loggero
    
from ppf import api
from ppf import config
from ppf.api import Data
from ppf import libs
from ppf.indexer import Index, Article, Articles
from ppf.tools.uploader import uploadFile

class MuseArticle(object):
    def __init__(self, doc_id):
        self.doc_id = doc_id
        self.filename = config.muses_d + str(doc_id) + config.muse_extension
        self.filename_html = config.muses_d + str(doc_id) + config.html_extension
        fd = open(self.filename, 'r')
        self.content = self.__replace_home(fd.read()) # The default is absolute path
        fd.close()

        self.json = self.getJson()
        self.html = self.getHtml()
        self.files = self.listImagesFromMuse(self.content) + \
            self.listFilesFromMuse(self.content)
        
    def getJson(self):
        article = Article()
        article.setFromId(self.doc_id)
        return article.__dict__

    def getHtml(self, hooks=True):
        content = self._html()
        if hooks:
            articleHook = config.ArticleHook()
            attr_names = libs.get_user_attributes(articleHook, False)
            for attr_name in attr_names:
                attr = getattr(articleHook, attr_name)
                if callable(attr):
                    attr()
                    continue
                regexp, str_replaced = attr
                content = re.sub(regexp, str_replaced, content)
        return content

    def _html(self):
        return self.getHtmlBody(self.filename_html)

    @classmethod
    def getHtmlBody(self, filename):
        fd = open(filename, 'r')
        content = fd.read()
        fd.close()

        try:
            body_start = re.search("<body>", content).end()
            body_end = re.search("</body>", content).start()
        except AttributeError:
            msg = filename + " has no body tag."
            config.logger.debug(msg)
            return content

        return content[body_start:body_end]
            
    
    # TODO: Consider elegant(?) way
    @staticmethod
    def getFullHtml(doc_id):
        filename = config.muses_d + str(doc_id) + config.html_extension
        fd = open(filename, 'r')
        content = fd.read()
        fd.close()
        try:
            body_start = re.search("<body>", content).end()
            body_end = re.search("</body>", content).start()
            body_end = body_end + len("</body>")
        except AttributeError:
            return None
        
        body = content[body_start:body_end]
        html_header = '''
<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8">

<link rel="stylesheet" type="text/css" href="../medias/css_body.css" />
<link rel="stylesheet" type="text/css" href="../medias/css_muse.css" />

<style type="text/css">
body {
  background: white; color: black;
  margin-left: 3%; margin-right: 7%;
  width:630px;
  border-style:solid;
  border-width:1px;
  padding:15px 19px 5px;
  
}
</style>


</head><body>
'''
        html_footer = "</html>"

        html = html_header + body + html_footer
        return html
        


    def listImages(self, html_source):
        '''
        Returns the image file names that are included in html.
        '''
        result = []
        matches = re.findall('<img src="[^"]*', html_source)
        for match in matches:
            filename = re.sub('<img src="', '', match)
            result.append(filename)
        return result

    def listImagesFromMuse(self, source):
        result = []
        dir_name = config.original_images_directory
        # We need to call self.__replace_home. Because the function file
        # will not read '~'. The default is absolute path in self.content
        dir_name = self.__replace_home(dir_name)

        reg = '\[\[' + dir_name + '[^\]]*'
        matches = re.findall(reg, source)
        for match in matches:
            filename = re.sub('\[\[', '', match)
            result.append(filename)

        return result

    def listFilesFromMuse(self, source):
        result = []
        dir_name = config.original_files_directory
        dir_name = self.__replace_home(dir_name)
        reg = '\[\[' + dir_name + '[^\]]*'
        matches = re.findall(reg, source)
        for match in matches:
            filename = re.sub('\[\[', '', match)
            result.append(filename)
        return result

    def __replace_home(self, path):
        home = os.environ['HOME']
        return re.sub('~/', home + '/', path)

    @classmethod
    def getFilename(self, ab_filename):
        '''
        Get filename from absoulte filename.
        '''
        filename_pt = ab_filename.rfind('/') + 1
        filename = ab_filename[filename_pt:]
        return filename
                


        


class API(object):

    """
    The class is used like urllib2.urlopen function with the arguments.
    The arguments specifies the data argument of urllib2.Request class. To
    create the arguments we use the class Data. The returned result is the
    returned result of urllib2.urlopen.

    """
    url = config.url_api

    def __init__(self, data):
        self.required_data = Data()
        # Set secure key
        self.required_data.secure_key = config.SECURE_KEY
        self.data = data
        self.cmd = self._getCmd()
        self._setArgs()
        #req = Request(self.url, self.required_data)
        #return urlopen(req)

    def _getCmd(self):
        try:
            return getattr(api, self.data.cmd)
        except AttributeError:
            raise AttributeError("'%s' requires data.cmd" % self.__class__.__name__)

    def _setArgs(self):
        # get the argument variable of self.cmd
        spec = inspect.getargspec(self.cmd)
        setattr(self.required_data, "cmd", self.data.cmd)
        for arg in spec.args:
            value = getattr(self.data, arg)
            setattr(self.required_data, arg, value)

    def send(self):
        data = self.required_data.urlencode()
        req = Request(self.url, data)
        #libs.log(req)
        return urlopen(req)
            
### apis
# TODO: We can create more simple apis.

#TODO: error handling.
def updateArticle(doc_id):
    """
    We use when an article is written/modified. It also update index. To
    use the function we need the muse file for index, the html file for
    article.
    >>> ma = MuseArticle('1201170413')    
    >>> #ma.html
    >>> #updateArticle('1201170413')
    """
    mu = MuseArticle(doc_id)
    index = mu.json
    html = mu.html
    files = mu.files

    # We have to update the index file both side client and server.
    # Because some functions of the client side requires index file such
    # as the function getUnupdatedArticles. That function is used to check
    # the articles that unpublished.

    # Client side only need index. The html created from emacs.
    article = Article()
    article.set(doc_id)
    article.updateFromDict(index)
    articles = Articles()
    articles.set()
    articles.updateFromObj(article)
    articles.save()

    # Server side need both index and html.
    updateIndex(doc_id, index)
    writeArticle(doc_id, html)
    if files:
        updateFiles(files)
    

def deleteComment(doc_id, comment_id):
    """
    deleteComment("0706012057", "26")
    """
    #libs.log(doc_id)
    #libs.log(comment_id)
    data = Data()
    data.cmd = "deleteComment"
    data.doc_id = doc_id
    data.comment_id = comment_id

    api = API(data)
    fd = api.send()
    result = fd.read()
    fd.close()
    return result

def writeComment(doc_id, _base64_content, _base64_name='', password=''):
    """
    >>> doc_id = '0706012057'
    >>> _base64_content = '어찌하다가 우리가 이런일에\\n 아'
    >>> _base64_name = '달수'
    >>> password = '12'
    >>> #dd = writeComment(doc_id, _base64_content, _base64_name, password)
    >>> #dd.read()
    >>> #'\\nOK\\n' # This is output
    """
    data = Data()
    data.cmd = "writeComment"
    data.doc_id = doc_id
    data._base64_content = _base64_content
    data._base64_name = _base64_name
    data.password = password

    api = API(data)
    fd = api.send()
    result = fd.read()
    fd.close()
    return result

def writeArticle(doc_id, _base64_content):
    """

    >>> doc_id = '0706012057'
    >>> _base64_content = '열라 테스트'
    >>> #ma = MuseArticle('1201170413')    
    >>> #ma.html
    >>> #dd = writeArticle('1201170413', ma.html)
    >>> #dd
    >>> #dd = writeArticle(doc_id, _base64_content)
    >>> #dd.read()
    >>> #'\\nOK\\n'

    """
    data = Data()
    data.cmd = "writeArticle"
    data.doc_id = doc_id
    data._base64_content = _base64_content

    api = API(data)
    fd = api.send()
    result = fd.read()
    fd.close()

    return result

def updateIndex(doc_id, _jsonBase64_dict):
    """

    >>> doc_id = '0706012057'
    >>> _jsonBase64_dict = {'category': 'emacs planner', 'date': '1108170951', 'author': 'this is author', 'update': '1108170952', 'title': '가나다 우리는 사는 사람들 이 닫 다다. fjdksf kdsf ', 'doc_id': '0706012057'}
    >>> #dd = updateIndex(doc_id, _jsonBase64_dict)
    >>> #dd.read()
    >>> #'\\nOK\\n'
    """

    data = Data()
    data.cmd = "updateIndex"
    data.doc_id = doc_id
    data._jsonBase64_dict = _jsonBase64_dict

    api = API(data)
    fd = api.send()
    result = fd.read()
    fd.close()
    return result


def updateFile(filename, _base64_content):
    '''
    Update files to the server. The file to be stored into config.files_d.
    '''
    data = Data()
    data.cmd = "updateFile"
    data.filename = filename
    data._base64_content = _base64_content

    # The server api will not replace the file. Returns False when The
    # file is exists in the server.
    api = API(data)
    fd = api.send()
    result = fd.read()
    return result

def updateFiles(files):
    'Update files from the list of file.'
    for f in files:
        fd = open(f, 'rb')
        content = fd.read()
        fd.close()

        # Get only filename. non-directory
        filename = MuseArticle.getFilename(f)
        updateFile(filename, content)


def updateServerFile(filename, _base64_content):
    """
    Client side function for the updateServer api.
    """
    data = Data()
    data.cmd = "updateServerFile"
    data.filename = filename
    data._base64_content = _base64_content

    api = API(data)
    fd = api.send()
    result = fd.read()
    fd.close()
    return result

def updateFileWithFtp(filename):
    """
    This function uses ftp to upload a file.
    """
    return uploadFile(filename)


def indexFilename():
    return config.index_filename()


def getArticleInfosAsJson (doc_id):
    article = Article()
    article.setFromId(doc_id)
    return json.dumps(article.__dict__)

def getFilename (id):
    '''
    >>> getFilename("1207262047") #doctest: +ELLIPSIS
    '/home/.../1207262047.muse'
    '''
    article = Article()
    return article._path(id)

def getConfig (attr, *args):
    '''
    >>> getConfig("index_filename") #doctest: +ELLIPSIS
    '/.../index.json'
    >>> getConfig("char_set")
    'utf-8'
    >>> getConfig("article_filename", "1207271735") #doctest: +ELLIPSIS
    '/.../1207271735.html'
    '''
    attr = getattr(config, attr)
    if callable(attr):
        if args:
            return attr(*args)
        else:
            return attr()
    else:
        return attr


### tools

def indexAllArticles():
    index = Index()
    index.create()

def getArticleHtml(doc_id):
    "Get the content of html verion of document."
    return MuseArticle.getFullHtml(doc_id)


def getUnupdatedArticles():
    """
    Returns a list of document id that is not contained in index.

    >>> getUnupdatedArticles() #doctest: +SKIP
    """

    articles = Articles()
    articles.set()
    article_table_updated = articles.json

    index = Index()
    article_table_all = index._create()

    for key in article_table_updated:
        if article_table_all.has_key(key):
            article_table_all.pop(key)
    return article_table_all.keys()



