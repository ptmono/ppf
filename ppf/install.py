#!/usr/bin/python
# coding: utf-8

import config

required_dirs = config.required_dirs
required_sys_files = config.required_sys_files
required_files = config.required_files

msg = ''
     

import cgitb
cgitb.enable()
import os
import stat


def fault_check_msg(filename):
    return "Checking %s: <b><font color='red'>fault</font></b><p>" % filename

def ok_check_msg(filename):
    return "Checking %s: OK<p>" % filename

def fault_create_file(filename):
    return "<font color='red'>Creating %s: fault</font><p>" % filename

def ok_create_file(filename):
    return "<font color='blue'>Creating %s: OK</font><p>" % filename

def check_and_make_directories():
    global msg
    global required_dirs
    for d in required_dirs:
        if os.path.exists(d):
            msg = msg + ok_check_msg(d)
        else:
            msg = msg + fault_check_msg(d)
            try:
                os.makedirs(d, 777)
                msg = msg + ok_create_file(d)
            except:
                msg = msg + fault_create_file(d)

def check_sys_files():
    global msg
    global required_sys_files
    for f in required_sys_files:
        if os.path.exists(f):
            msg = msg + ok_check_msg(f)
        else:
            msg = msg + fault_check_msg(f)

def check_files():
    global msg
    global required_files
    for f in required_files:
        if os.path.exists(f):
            msg = msg + ok_check_msg(f)
        else:
            msg = msg + fault_check_msg(f)
            # Init the database directory.
            for filename, content in required_files[f]:
                create_file(filename, content)
                msg = msg + ok_create_file(filename)


def init_db():
    'We need to initiate the index file when firstly server is uploaded.'
    global required_files
    for f in required_files:
        for filename, content in required_files[f]:
            create_file(filename, content)
    
                
def create_file(ab_filename, content):
    dirname = ab_filename[:ab_filename.rfind('/')]
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    fd = open(ab_filename, 'w')
    fd.write(content)
    fd.close()

    st = os.stat(ab_filename)
    os.chmod(ab_filename, st.st_mode | stat.S_IWOTH)    

def main():
    if os.path.exists(config.installed_checkp):
        return "If you want to re-install, delete '%s' file" % config.installed_check_file
    global msg
    check_and_make_directories()
    check_sys_files()
    check_files()

    fd = open(config.installed_checkp, 'w')
    fd.close()

    return msg

if __name__ == "__main__":
    main()
