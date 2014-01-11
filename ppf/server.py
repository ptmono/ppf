#!/usr/bin/python
# coding: utf-8

import sys

import cgi
import cgitb
cgitb.enable()

from .viewer import View
from . import libs
from . import config



def main():
    libs.waitUnlock()
    form = cgi.FieldStorage()
    view = View()
    view.show(form)


if __name__ == '__main__':
    main()
    
