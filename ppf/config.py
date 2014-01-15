#!/usr/bin/python
# coding: utf-8

from __future__ import unicode_literals
import os.path
from os.path import dirname, abspath, realpath
import sys

ZIP_SOURCE = False
UPLOAD_ZIP_SOURCE = False

#current_abpath = '/home/ptmono/public_html/0ttd/0ppf2/server/'
__current_abpath = realpath(dirname(__file__)) + "/"
root_abpath = os.path.dirname(os.path.dirname(__current_abpath))

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
muses_d = os.path.join(root_abpath, dbs_d)

# The htmls directory contains html file which converted from the original
# article.
htmls_d = os.path.join(root_abpath, 'htmls/')

# The comment directory contains comment db file.
comments_d = os.path.join(root_abpath, htmls_d)

# The medias directory contains html templates, css, js files.
medias_d = os.path.join(root_abpath, 'medias/')

# The files directory contains the image files that used by the web
# content, the files will can be downloaded by user.
files_d = os.path.join(root_abpath, 'files/')

# 3rd party modules
modules_d = os.path.join(root_abpath, 'modules/')
set_path = set(sys.path)
if not modules_d in set_path: sys.path.insert(0, modules_d)
    
# The file name of recent comments db.
recent_comments_db = os.path.join(dbs_d, 'recent_comments_db')

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
template_all_l = os.path.join(medias_d, 'jinja_list.html')

# welcome file
welcome_file = os.path.join(root_abpath, 'README')

# Maximum comment count. Article's climit determines that.
max_comments = '20'

# This file is created when you have installed the pages.
installed_check_file = '0installed'
installed_checkp = os.path.join(htmls_d, installed_check_file)


ERRORP = False
WARNP = True

char_set = 'utf-8'

# If you posting an article, the client uses this key as the password.
SECURE_KEY = '66b43ed7577cb74511fa6a5836f613448b4f47dc'

update_lock_filename = os.path.join(root_abpath, "updating")


def article_filename(doc_id):
    "Full path of article."
    return os.path.join(htmls_d, doc_id + html_extension)

def comment_filename(doc_id):
    "Full path of comment of article."
    return os.path.join(comments_d, doc_id + comment_extension)

def index_filename():
    "Full path of the table of articles."
    return os.path.join(htmls_d, index_file)

def recent_comment_filename():
    return os.path.join(comments_d, recent_comments_db)


def read_welcome():
    try:
        fd = open(welcome_file, 'r')
    except IOError:
        return ''
    content = fd.read()
    content = content.replace('\n', '<br>')
    return content


class ArticleHook:
    '''We can edit or any action before for updating html. It applied to html
    file.

    - replacement: add tuple attribute
     - action: add function

     e.g) 

     'image_name = "/home/ptmono/.emacs.d/imgs", "files")' will replace
     "/home/ptmono/.emacs.d/imgs" as "files".

     or

     image_name = "replace_image_url"
     defun replace_image_url(self):
           _repalce_image_url()
    '''
    # Fixme: Solve globally the ~ problem.
    image_name = ("/home/ptmono/.emacs.d/imgs", "/files")
    image_name2 = ("~/.emacs.d/imgs", "/files")
    file_name = ("/home/ptmono/files", "/files")
    file_name2 = ("~/files", "/files")



###
### === Logger
### ______________________________________________________________
import logging

LOG_TO_FILEP = True
if LOG_TO_FILEP:
    LOG_FILE_FILENAME = os.path.join(root_abpath, dbs_d, 'logging.log')
    LOG_FILE_MODE = 'a'
else:
    LOG_FILE_FILENAME = None
    LOG_FILE_MODE = None

LOG_FORMAT = '%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s'
LOG_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
LOG_LEVEL = logging.DEBUG

# To solve permission problem we need to execute install.py
logging.basicConfig(filename=LOG_FILE_FILENAME,
                    filemode=LOG_FILE_MODE,
                    format=LOG_FORMAT,
                    datefmt=LOG_TIME_FORMAT,
                    level=LOG_LEVEL)
logger = logging.getLogger('ppf')    

### === Mail
### --------------------------------------------------------------
comment_mail_me = False
email_admin = "ptmono@localhost"
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



try:
    from . import config_priv
    usr_root		= config_priv.url_root
    url_api		= config_priv.url_api
    server_host 	= config_priv.server_host
    server_user_id	= config_priv.server_user_id
    server_passwd	= config_priv.server_passwd
    server_root_directory = config_priv.server_root_directory
    
except Exception as err:
    usr_root		= ''
    url_api			= ''
    server_host 	= ''
    server_user_id	= ''
    server_passwd	= ''
    server_root_directory = ''

    

# Muse uses the images of this directory. The images of article will be
# duplicated into dbs_d.
original_images_directory = '~/.emacs.d/imgs/'
# Muse uses the files of this directory. The file links of article that we
# want to upload will be duplicated into dbs_d.
original_files_directory = '/home/ptmono/files/'


list_of_files_to_be_installed = os.path.join(root_abpath, 'ppf/tools', 'installer_file_list')


### for install

# The directories can be writable.
required_dirs = \
    [muses_d, htmls_d, comments_d, files_d]
     
required_sys_files = \
    [template_all_l]

# The files to be initiated
required_files = \
    {index_filename():
     [(index_filename(),'{"0000000001" : {"category": "a", "title":"Welcome"}}'),
      (htmls_d + "0000000001" + html_extension, read_welcome())]
     }


### === ppfjob
### ______________________________________________________________
PPFJOB_LOCAL_MODE = False
