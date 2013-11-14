#!/usr/bin/python
# coding: utf-8

import os
import time
import sys
import re
import logging
import fnmatch

import config
import html_messages as hm




def openFileSafely(filename):
    try:
        fd = file(filename, 'r')
        contents = fd.write(fd.read())
        fd.close()

    except IOError:
        # there is no filename
        contents = ''

    # backup
    backup_filename = _backupFileName(filename)
    fd_bak = file(backup_filename, 'w')
    fd_bak.write(contents)
    fd_bak.close()

    fd = file(filename, 'w')
    return fd

def _backupFileName(filename):
    return "#" + filename + "#"


# TODO: I need more reuseable/stable logging method. Consider logging
# module.

#Obsoleted. Use config.logger
def log(msg):
    t = time.strftime("%Y-%m-%d %H:%M:%S")
    msg = "LOG[" + t + "]: " + msg + "\n"
    if config.ERRORP:
        print msg
    else:
        fd = file(config.log_file, 'a')
        fd.write(msg)

#Obsoleted. Use config.logger
def logError(msg):
    t = time.strftime("%Y-%m-%d %H:%M:%S")
    msg = "ERROR[" + t + "]: " + msg + "\n"
    if config.ERRORP:
        print msg
    else:
        fd = file(config.log_file, 'a')
        fd.write(msg)


def textExt(p):
    """
    Returns the extension of string
    >>> aa = '/usr/local/abc.py'
    >>> textExt(aa)
    'py'
    >>> aa = '/usr/local/abc'
    >>> textExt(aa)
    ''
    """
    extsep = '.'
    dotIndex = p.rfind(extsep)
    if dotIndex == -1:
        # There  is no extension                    
        return ''
    extIndex = dotIndex + 1
    return p[extIndex:]

def removeBlank(aa):
    return aa.replace('\n', '')

# from web
def strcut_utf8(str, destlen, checkmb=True, tail=""):
    """
    UTF-8 Format
    0xxxxxxx = ASCII, 110xxxxx 10xxxxxx or 1110xxxx 10xxxxxx 10xxxxxx
    라틴 문자, 그리스 문자, 키릴 문자, 콥트 문자, 아르메니아 문자, 히브리 문자, 아랍 문자 는 2바이트
    BMP(Basic Mulitilingual Plane) 안에 들어 있는 것은 3바이트(한글, 일본어 포함)
    """
    slen = len(str)
    tlen = len(tail)
    
    if slen <= destlen:
        return str
    
    pattern = "[\xE0-\xFF][\x80-\xFF][\x80-\xFF]"
    count=0
    text = []
    for match in re.finditer(pattern, str):
        if len(checkmb == True and match.group(0)) > 1:
            count = count + 2
        else:
            count = count + 1
        if (count + tlen) > destlen:
            return "".join(text) + tail
        text.append(match.group(0))
            
    return "".join(text)
        

def waitUnlock():
    """
    Wait unlock the site. Allmost site lock is used for updating site. It
    seems end less than 2 second.
    """ 
    if os.path.exists(config.update_lock_filename):
        filep = True
        counter = 6
        while counter:
            time.sleep(0.3)
            if os.path.exists(config.update_lock_filename):
                counter -= 1
                continue
            filep = False
            break
        if filep:
            print hm.redirect_wait_updating
            sys.exit(1)


def lock():
    "It is used to lock the site."
    fd = file(config.update_lock_filename, 'w')
    fd.close()

def unlock():
    os.remove(config.update_lock_filename)


def get_user_attributes(cls, exclude_methods=True):
    '''
    Get user the defined attributes from class.
    '''
    base_attrs = dir(type('dummy', (object,), {}))
    this_cls_attrs = dir(cls)
    res = []
    for attr in this_cls_attrs:
        if base_attrs.count(attr) or (callable(getattr(cls, attr)) and exclude_methods):
            continue
        res += [attr]
    return res
