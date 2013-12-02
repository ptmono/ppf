#!/usr/bin/python
# coding: utf-8

import sys
import config

import cgi
import cgitb
cgitb.enable()

import libs
from viewer import View

def main():
    libs.waitUnlock()
    form = cgi.FieldStorage()
    view = View()
    view.show(form)


if __name__ == '__main__':
    main()
    
