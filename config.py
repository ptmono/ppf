#!/usr/bin/python
# coding: utf-8

from os.path import dirname, abspath
import sys

ZIP_SOURCE = False
UPLOAD_ZIP_SOURCE = False

#current_abpath = '/home/USER_ID/public_html/0ttd/0ppf2/server/'
current_abpath = abspath(dirname(__file__)) + "/"


# The list of header of article. Each header contains the information of
# the article. e.g) climit restrict the number of comment.
article_informations = ["doc_id", "title", "author", "date", "update",
                        "tag", "category", "unpublished", "climit"]

# obsolete
update_file = 'update.json'

# The site uses indexing of articles. This is the filename.
index_file = 'index.json'

# I use common database directory.
dbs_d = 'dbs/'

# The muses directory contains original articles.
muses_d = current_abpath + dbs_d

# The htmls directory contains html file which converted from the original
# article.
htmls_d = current_abpath + dbs_d

# The comment directory contains comment db file.
comments_d = current_abpath + dbs_d

# The medias directory contains html templates, css, js files.
medias_d = current_abpath + 'medias/'

# The files directory contains the image files that used by the web
# content, the files will can be downloaded by user.
files_d = current_abpath + 'files/'

# 3rd party modules
modules_d = current_abpath + 'modules/'
set_path = set(sys.path)
if not modules_d in set_path: sys.path.insert(0, modules_d)
    
# The file name of recent comments db.
recent_comments_db = 'recent_comments_db'

# The extension of original file
muse_extension = ".muse"
# The extension of html file
html_extension = ".html"
# The extension of comment file
comment_extension = ".txt"

# obsolete
html_header = medias_d + "basic_header.html"
html_footer = medias_d + "basic_footer.html"


# html template for home(obsolete)
# template_home = medias_d + 'jinja_home.html'

# html template for the list of article
template_all_l = medias_d + 'jinja_list.html'

# welcome file
welcome_file = current_abpath + 'README'

# Maximum comment count. Article's climit determines that.
max_comments = '20'

# This file is created when you have installed the pages.
installed_check_file = '0installed'
installed_checkp = current_abpath + dbs_d + installed_check_file


ERRORP = False
WARNP = True

char_set = 'utf-8'

# If you posting an article, the client uses this key as the password.
SECURE_KEY = '66b43ed7577cb74511fa6a5836f613448b4f47dc'

update_lock_filename = current_abpath + "updating"


def article_filename(doc_id):
    "Full path of article."
    return htmls_d + doc_id + html_extension

def comment_filename(doc_id):
    "Full path of comment of article."
    return comments_d + doc_id + comment_extension

def index_filename():
    "Full path of the table of articles."
    return muses_d + index_file

def recent_comment_filename():
    return comments_d + recent_comments_db


def read_welcome():
    fd = open(welcome_file, 'r')
    content = fd.read()
    content = content.replace('\n', '<br>')
    return content


class ArticleHook:
    '''We can edit or any action before for updating html. It applied to html
    file.

    - replacement: add tuple attribute
     - action: add function

     e.g) 

     'image_name = "/home/USER_ID/.emacs.d/imgs", "files")' will replace
     "/home/USER_ID/.emacs.d/imgs" as "files".

     or

     image_name = "replace_image_url"
     defun replace_image_url(self):
           _repalce_image_url()
    '''
    # Fixme: Solve globally the ~ problem.
    image_name = ("/home/USER_ID/.emacs.d/imgs", "files")
    image_name2 = ("~/.emacs.d/imgs", "files")
    file_name = ("/home/USER_ID/files", "files")
    file_name2 = ("~/files", "files")


###
### === Logger
### ______________________________________________________________
import logging

LOG_TO_FILEP = True
if LOG_TO_FILEP:
    LOG_FILE_FILENAME = current_abpath + dbs_d + 'logging.log'
    LOG_FILE_MODE = 'a'
else:
    LOG_FILE_FILENAME = None
    LOG_FILE_MODE = None

LOG_FORMAT = '%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s'
LOG_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
LOG_LEVEL = logging.DEBUG

# logger doesn't create rw-rw-rw. Manually change the permission
logging.basicConfig(filename=LOG_FILE_FILENAME,
                    filemode=LOG_FILE_MODE,
                    format=LOG_FORMAT,
                    datefmt=LOG_TIME_FORMAT,
                    level=LOG_LEVEL)
# except:
#     import os
#     os.chmod(LOG_FILE_FILENAME, 0777)
    
    
logger = logging.getLogger('ppf')


### === Mail
### --------------------------------------------------------------
comment_mail_me = False
email_admin = "USER_ID@localhost"
email_site = "ppf@ppf.pe.kr"
# smtp type. 'gmail', 'local'.If you use 'gmail' smtp, we requires
# gmail_user and gmail_password
mail_client = 'local' # 'gmail', 'local'.
gmail_user = ''
gmail_password = ''


### client side only
# This configuration will help the use of ./tools/uploader.py. uploader.py
# will upload ppf into web server with ftp. The server have to turn on the
# ftp server.

LOCAL_TEST=True
# url_root : The url of page

if LOCAL_TEST:
    url_root = "http://localhost/~USER_ID/0ttd/0ppf2/ppf/"
    url_api = url_root + "api.py"
    server_host = "localhost"
    server_user_id  = "USER_ID"
    server_passwd = "USER_PASSWORD"
    server_root_directory = '/home/USER_ID/public_html/0ttd/0ppf2/ppf'

else:
    url_root = "http://USER_ID.linuxstudy.pe.kr/ppf/"
    url_api = url_root + "api.py"
    server_host = "USER_ID.linuxstudy.pe.kr"
    server_user_id  = "USER_ID"
    server_passwd = "USER_PASSWORD"
    # Any ftp host's root directory start from '/'. 
    server_root_directory = '/public_html/ppf'
    #server_root_directory = '/home/member/USER_ID/public_html/ppf'

# Muse uses the images of this directory. The images of article will be
# duplicated into dbs_d.
original_images_directory = '~/.emacs.d/imgs/'
# Muse uses the files of this directory. The file links of article that we
# want to upload will be duplicated into dbs_d.
original_files_directory = '/home/USER_ID/files/'


list_of_files_to_be_installed = current_abpath + 'tools/' + 'installer_file_list'


### for install

# The directories can be writable.
required_dirs = \
    [muses_d, htmls_d, comments_d, files_d]
     
required_sys_files = \
    ['api.py', 'config.py', 'html_messages.py', 'indexer.py',
     'libs.py', 'poster.py', 'server.py', 'viewer.py',
     template_all_l]

# The files to be initiated
required_files = \
    {index_filename():
     [(index_filename(),'{"0000000001" : {"category": "a", "title":"Welcome"}}'),
      (htmls_d + "0000000001" + html_extension, read_welcome())]
     }
