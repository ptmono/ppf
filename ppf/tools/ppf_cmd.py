#!/usr/bin/python
# coding: utf-8

import sys

from uploader import uploadFile


class Cmds(object):

    def uploadFile(self, name):
        uploadFile(name)

def main():
    func_name = sys.argv[1]
    arg = sys.argv[2]
    cmds = Cmds()
    func = getattr(cmds, func_name)
    func(arg)

if __name__ == "__main__":
    main()
