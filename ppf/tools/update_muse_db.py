#!/usr/bin/python
# coding: utf-8


import os, sys

lib_path = os.path.abspath('..')
if lib_path not in sys.path:
    sys.path.insert(0, lib_path)

import indexer


def main():
    indexObj = indexer.Index()
    indexObj.create()

if __name__ == "__main__":
    main()
