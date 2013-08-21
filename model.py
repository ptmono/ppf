#!/usr/bin/python
# coding: utf-8

import re
import itertools

from dlibs.common import *
from dlibs.logger import logger, loggero

def parseAttr(obj, regexp, num):
    result = {}
    pattern = re.compile(regexp)
    for a in dir(obj):
        match = pattern.match(a)
        if match:
            element = match.group(num)
            # only lower first char
            element = element[0].lower() + element[1:]
            result[element] = a
    return result

def generate_urls(url_format, url_range):
    """
    We can generate urls from URL_FORMAT and URL_RANGE. Follow the
    example.

    URL_FORMAT %s will be replaced with url_range. e.g)
    'http://example.com/%s/%s'
    
    URL_RANGE can be a list of list. e.g) [[range(4)], [range(1, 7),
    range(5, 9)]]

    It returns a generator. 

    """
    for ele in product_generator(url_range):
        result = url_format % ele
        yield result
    

def product_generator(url_range):
    # It is used in GetSetModel to set _set__urls.
    number_of_args = len(url_range)
    formated_lists = []

    for ran in url_range:
        # Merge sublists
        ele = merge_lists(ran)
        formated_lists.append(ele)

    return itertools.product(*formated_lists)

def merge_lists(alist):
    """
    >>> aa = [range(8), range(7, 16), range(19, 21)]
    >>> merge_lists(aa)
    [0, 1, 2, 3, 4, 5, 6, 7, 7, 8, 9, 10, 11, 12, 13, 14, 15, 19, 20]
    
    """
    try:
        return [x for sublist in alist for x in sublist]
    except TypeError as err:
            if str(err)[1:4] == 'int':
                return alist
            else: raise TypeError(str(err))


def list_range_to_list(ran):
    """
    Following examples shows how this function works.

    >>> list_range_to_list([1, 10])
    [1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> list_range_to_list([[1, 5]])
    [1, 2, 3, 4]
    >>> list_range_to_list([[1,4], [6,8], [12,18]])
    [1, 2, 3, 6, 7, 12, 13, 14, 15, 16, 17]
    >>> list_range_to_list(['a', 'b']) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ValueError: need more than 1 value to unpack

    """
    result = []
    start = 0
    stop = 0
    for r in ran:
        try:
            start, stop = r
        except TypeError as err:
            if str(err)[1:4] == 'int':
                start, stop = ran
                return [ a for a in xrange(start, stop) ]
            else:
                raise TypeError(str(err))
            
        for a in xrange(start, stop):
            result.append(a)
    return result



class GetMixin(object):
    """

    Determine self._source and self._info['columns']. This mixin
    requires ModelStructureA.

    self._info['columns'] contains a dictionary that contains the
    information of the get prefixed methods. e.g) {'url': 'getUrl',
    'title': 'getTitle'} where value is the name of method.

    self.source is created when self.get is called. All get prefixed
    methods assume that the model provides self._source.

    self.get method defines how the self._source is parsed with the get
    prefixed methods.

    

    """
    def _set_columns(self):
        self._info['columns'] = parseAttr(self, 'get(\w+)', 1)

    def get(self, source):
        self.source = source
        result = {}
        for col in self._info['columns']:
            func = getattr(self, self._info['columns'][col])
            parsed_result = func()
            result[col] = parsed_result
        return result

    def list(self, source):
        info = self.get(source)
        return self.infoToList(info)


    @classmethod
    def infoToList(self, info):
        zipped_cols = zip(*(info[col] for col in info))
        return zipped_cols

    def columns(self):
        return list(self._info['columns'])
            

class GetSetMixin(GetMixin):
    """
    Determine self._columns. We also declare self._variables.

    self._variables --> local variables which will be the attribute of object
    """

    def _set_variables(self):
        self._info["variables"] = parseAttr(self, 'set(\w+)', 1)

    def get(self, source):
        self.source = source
        self.init_get()
        result = {}

        # Set variables
        for var in self._info['variables']:
            method = getattr(self, self._info['variables'][var])
            value = method()
            try:
                getattr(self, var)
                msg = "We couldn't set %s." % var
                raise NameError(msg)
            except:
                setattr(self, var, value)

        # Parse
        for col in self._info['columns']:
            func = getattr(self, self._info['columns'][col])
            parsed_result = func()
            # returned type is lxml.etree._ElementUnicodeResult
            # To deal easy, convert to unicode
            try:
                result[col] = [unicode(ele) for ele in parsed_result]
            except NameError:
                result[col] = [str(ele) for ele in parsed_result]
        return result

    def init_get(self):
        """It is pre hook for self.source or get method"""
        pass
        

class UrlsMixin(object):
    """
    Determine self._urls

    To determine self._urls the class has following attribute
     - url_format and url_range
     - urls
    """
    def _set_urls(self):

        url_attrs = {"urls": False, "url_format": False, "url_range": False}

        for attr in url_attrs:
            try:
                getattr(self, attr)
                url_attrs[attr] = True
            except AttributeError:
                pass

        if url_attrs["urls"]:
            self._info["urls"] = self.urls
        elif url_attrs["url_format"] and url_attrs["url_range"]:
            self._info["urls"] = generate_urls(self.url_format, self.url_range)
        else:
            self._info["urls"] = []
            loggero().debug(self.__class__.__name__ + " has no urls! and url_format is %s" % str(url_attrs['url_format']))
            

class ModelStructureA(object):
    """
    To create model we use
     - "_" prefix variable
     - "_set_" prefix method to set variable.

    self._columns --> A list of column which will be the column of database
    self._urls --> urls we will parse

    self._columns will be used for the columns of database and the
    method of parsing. The mehod can be specified by MixIn classes such
    as GetSetMixIn.

    """

    def __init__(self):
        self._info = {}

        super(ModelStructureA, self).__init__()
        self._init()
    
    def _init(self):
        for attr in dir(self):
            if attr[:5] == "_set_":
                func = getattr(self, attr)
                func()

                
class GetSetModel(ModelStructureA, GetSetMixin, UrlsMixin):
    pass


