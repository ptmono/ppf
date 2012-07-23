#!/usr/bin/python
# coding: utf-8

'''
This module is obsoleted. See indexer.py
'''


import config, libs

import json
import os


# [object1, object2, object3, ... , OBJECTN]
# OBJECT
# {DOCNUMBER: DOCUMENT}



class Var:
    output = []
    update_file = config.update_file
    index_file = config.index_file


class Basic(object):
    file_info = config.article_informations

    def __init__(self):
        self.create_local_variables()

    def __repr__(self):
        return repr(self.__dict__)

    def create_local_variables(self):
        for name in self.file_info:
            setattr(self, name, '')

    def encodeJson(self):
        return self.__dict__


class File(Basic):

    def __init__(self, doc_number):
        super(File, self).__init__()
        self.doc_number = str(doc_number)
        instance_element = {self.doc_number: self.__dict__}
        Var.output.append(instance_element)


def clear():
    Var.output = []
    return Var.output

def _saveCommon(filename):
    json_dump = json.dumps(Var.output)
    fd = libs.openFileSafely(filename)
    fd.write(json_dump)
    fd.close()

    os.remove(_backupFileName(filename))
    

def _loadCommon(filename):
    fd = file(filename, 'r')
    content = fd.read()
    fd.close()
    json_load = json.loads(content)
    Var.output = json_load

def saveUpdate():
    _saveCommon(Var.update_file)
    return Var.output


def loadUpdate():
    _loadCommon(Var.update_file)
    return Var.output

def saveIndex():
    _saveCommon(Var.index_file)

def loadIndex():
    _loadCommon(Var.index_file)
    

def sortJson(json_load):
    return sorted(json_load)

