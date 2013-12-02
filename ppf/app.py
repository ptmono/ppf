#!/usr/bin/env python
# coding: utf-8

from flask import Flask, request

from viewer import ViewHome, ViewId, ViewAll
from poster import addComment_wsgi

import config

#app = Flask(__name__, static_folder=config.medias_d)
app = Flask(__name__)
app.debug = True

from werkzeug import SharedDataMiddleware
import os

app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/medias':	config.medias_d,
    '/files':	config.files_d
    })

@app.route('/home')
@app.route('/')
def home():
    home = ViewHome()
    return home.show()

@app.route('/article/<doc_id>')
def article_doc(doc_id):
    doc = ViewId(doc_id)
    return doc.show()

@app.route('/all')
@app.route('/article/all')
def article_all():
    docs = ViewAll()
    return docs.show()


@app.route('/writecomment', methods=["POST"])
def write_comment():

    return addComment_wsgi(request)

if __name__ == '__main__':
    app.run(port=3108)
