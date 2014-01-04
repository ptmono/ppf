#!/usr/bin/python
# coding: utf-8

try:
    from urlparse import urlparse
    from urllib import unquote
except ImportError:
    from urllib.parse import urlparse
    from urllib.parse import unquote
    
from cgi import parse_qs


from lxml.cssselect import CSSSelector
from lxml.html import parse, fromstring, tostring

import requests
import re
import os

from sqlalchemy import MetaData, create_engine, Table
from sqlalchemy.orm import sessionmaker, mapper

from dlibs.logger import loggero


def db_print(engine_name, table_name, attrs, tid):
    engine = create_engine(engine_name)
    class Post(object): pass
    metadata = MetaData(engine)
    post_table = Table(table_name, metadata, autoload=True)

    mapper(Post, post_table)

    Session = sessionmaker(bind=engine)
    session = Session()

    one = session.query(Post).filter_by(_id=tid).one()

    for attr in attrs:
        func = getattr(one, attr)
        print(func)
        
    

class NetTools:

    @classmethod
    def save_page(self, url, filename):
        r = requests.get(url)
        data = r.content
        fd = open(filename, 'w')
        try:
            fd.write(data)
        except TypeError:
            fd = open(filename, 'bw')
            fd.write(data)

        fd.close()

    @classmethod
    def read(self, path):
        if path[:4] == 'http':
            r = requests.get(path)
            data = r.content
            return data
        try:
            fd = open(path, 'r')
            return fd.read()
        except UnicodeDecodeError:
            fd = open(path, 'br')
            return fd.read()
            

    
class CssParsers:
    @classmethod
    def first_content(self, data, selector):
        selector = (selector)
        sel = CSSSelector(selector)
        sel_list = sel(fromstring(data))
        content = sel_list[0].text_content()
        return content

    @classmethod
    def css_content(self, data, selector, num=0, removetabs=False):
        selector = (selector)
        sel = CSSSelector(selector)
        sel_list = sel(fromstring(data))
        content = sel_list[num].text_content()
        if removetabs:
            content = self.remove_tabs(content)
        return content

    @classmethod
    def css_all_content(self, data, selector, removetabs=False):
        """
        It seems so slow. Consider to use xpath_all_content.
        
        """
        result = []
        sel = CSSSelector(selector)
        try:
            sel_list = sel(fromstring(data))
        except TypeError:
            sel_list = sel(data)
        for sel in sel_list:
            try:
                data = sel.text_content()
            except AttributeError:
                data = sel.text
            if removetabs:
                data = self.remove_tabs(data)
            result.append(data)
        return result

    @classmethod
    def css_all_getattr(self, data, selector, attr, prefix="", subfix=""):
        result = []
        sel = CSSSelector(selector)
        sel_list = sel(fromstring(data))
        for sel in sel_list:
            ele = prefix + sel.get(attr) + subfix
        return result

    @classmethod
    def css_getattr(self, data, selector, attr, num=0):
        result = []
        sel = CSSSelector(selector)
        sel_list = sel(fromstring(data))
        return sel_list[num].get(attr)
    
    @classmethod
    def all_content(self, data, selector):
        result = []
        sel = CSSSelector(selector)
        sel_list = sel(fromstring(data))
        for sel in sel_list:
            title = sel.text_content()
            result.append(title)
        return result
        
    @classmethod
    def remove_tabs(self, content):
        try:
            return re.sub("[\r\n\t]*", "", content)
        except:
            return ""


    @classmethod
    def xpath_all_content(self, tree, xpath, removetabs=False):
        result = []
        sel_list = tree.xpath(xpath)
        for s in sel_list:
            data = s.text
            if removetabs:
                data = self.remove_tabs(data)
            result.append(data)
        return result

def parseURL(url):
    """
    Parses a URL as a tuple (host, path, args) where args is a
    dictionary.

    """


    scheme, host, path, params, query, hash = urlparse(url)
    if not path: path = "/"

    args = parse_qs(query)

    escapedArgs = {}
    for name in args:
        if len(args[name]) == 1:
            escapedArgs[unquote(name)] = unquote(args[name][0])
        else:
            escapedArgs[unquote(name)] = escapedSet = []
            for item in args[name]:
                escapedSet.append(unquote(item))

    return host, path, params, escapedArgs


    


class TestingMixin(object):
    @classmethod
    def _dummy_data(self, filename=None):
        if not filename:
            filename = self._generate_filename()
        return NetTools.read(filename)

    @classmethod
    def _save_dummy_data(self, filename=None):
        if not filename:
            filename = self._generate_filename()
        NetTools.save_page(self.urls[0], filename)

    @classmethod
    def _generate_filename(self):
        dir = os.getcwd()
        filename = self.__name__ + '_sample.html'
        result = os.path.join(dir, '__tmp/' + filename)
        return result



