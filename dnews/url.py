import re
import itertools

from dlibs.common import *
from dlibs.logger import loggero


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
            return list(alist)
        else: raise TypeError(err)


def list_range_to_list(ran):
    """
    Following examples shows how this function works.

    >>> list_range_to_list([1, 10]) 
    [1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> list_range_to_list([[1, 5]]) #doctest: +SKIP
    [1, 2, 3, 4]
    >>> list_range_to_list([[1,4], [6,8], [12,18]]) #doctest: +SKIP
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
                raise(err)
            
        for a in xrange(start, stop):
            result.append(a)
    return result


class UrlsMixin(object):
    """
    Determine self._urls

    To determine self._urls the class has following attribute
     - url_format and url_range
     - urls
    """
    def _set_urls(self):
        try:
            if self.url_format and self.url_range:
                self._info["urls"] = generate_urls(self.url_format, self.url_range)
        except AttributeError as err:
            if str(err).find("url_format") is not -1:
                try:
                    self._info["urls"] = self.urls
                except:
                    msg = repr(err).replace("'url_format'", "'urls' or 'url_format' 'url_range'")
                    raise AttributeError(msg)

