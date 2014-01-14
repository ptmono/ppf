#!/usr/bin/python
# coding: utf-8

import os, sys

lib_path = os.path.abspath('..')
if lib_path not in sys.path:
    sys.path.insert(0, lib_path)

from indexer import Comments
import config


def main():
    json = {'1': {'date': '11/08/31', 'name': 'Talsu', 'password': 'a', 'content': '이건 이런 있을 수 없는 일 잉 있나 오옹오오 그러 나 하지만 업수로 아작'}, '2': {'date': '11/09/31', 'name': 'Tal', 'password': 'a', 'content': '이건 이런 있을 수 없는 일 잉 있나 오옹오오 그러 나 하지만 업수로 아작'}, '3': {'date': '11/09/20', 'name': 'dalsoo', 'password': 'a', 'content': '그러 나 하지만 업수로 아작'}}


    comments = Comments('0706012057')
    comments.setFromDict(json)
    comments.save()
    

if __name__ == "__main__":
    main()
