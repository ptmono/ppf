#!/usr/bin/env python
# coding: utf-8

from flask import Flask, request
app = Flask(__name__)
app.debug = True

import config

from viewer import ViewHome, ViewId, ViewAll
from poster import addComment_wsgi
import api

from werkzeug import SharedDataMiddleware
import os

app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/medias':	config.medias_d,
    '/files':	config.files_d
    })


@app.route('/home')
@app.route('/')
def home():
    try:
        home = ViewHome()
        return home.show()
    except IOError as err:
        if _checkArticleIndex(err):
            # There is no index file
            #_initArticleIndex()
            # import install
            # return install.main()
            raise InitError()
        raise IOError(str(err))


@app.route('/article/<doc_id>')
def article_doc(doc_id):
    doc = ViewId(doc_id)
    return doc.show()

@app.route('/all')
@app.route('/article/all')
def article_all():
    docs = ViewAll()
    return docs.show()

@app.route('/api', methods=["POST"])
def use_api():
    return api.main_wsgi(request)

@app.route('/writecomment', methods=["POST"])
def write_comment():

    return addComment_wsgi(request)


@app.route('/error/permission_log')
def error_permission_log():
    return "akfksdksfksf"


def _checkArticleIndex(err_msg):
    msg = str(err_msg)
    if msg.find(config.index_file) == -1:
        return False
    return True

from app_exceptions import InitError

@app.errorhandler(InitError)
def handle_init_error(error):
    import install
    return install.main()



if __name__ == '__main__':
    app.run(port=3108)
