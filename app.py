#!/usr/bin/env python
# coding: utf-8

import sys
import os

from flask import Flask, request, render_template, flash, redirect, url_for, g, session
from flask.ext.cache import Cache
from flask.ext.login import login_required, current_user, logout_user

from ppf import config
from ppf import api
from ppf.viewer import ViewHome, ViewId, ViewAll
from ppf.viewer import JinjaEnvironment
from ppf.poster import addComment_wsgi
from ppf.app_exceptions import InitError, PageNotFound

from ppfjob.views import jobs_filtered, job_page
from ppfjob.models import Jobs, Jobsearches

from ppfadmin.views import ppfadmin_login, ppfadmin_join
from ppfadmin.models import init_login, db, LoginForm

from werkzeug import SharedDataMiddleware

from dnews.scraper		import Scraper
from dScraper.container.saramin import SaraminItModel

import logging

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
app.debug = True

cache = Cache(app, config={'CACHE_TYPE': 'null'})

app.config['SECRET_KEY'] = '0000000000'
app.config['DATABASE_FILE'] = 'sample_db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
app.config['SQLALCHEMY_ECHO'] = True


app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/medias':	config.medias_d,
    '/files':	config.files_d
    })



db.init_app(app)
db.create_all(app=app)
init_login(app)


@app.route("/login", methods=["GET", "POST"])
def login():
    return ppfadmin_login(request)

@app.route("/join", methods=["GET", "POST"])
def join():
    return ppfadmin_join(request)

@app.route("/settings")
@login_required
def settings():
    pass

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(request.args.get("next") or url_for('home'))


@app.route('/home')
@app.route('/')
@cache.memoize(3000)
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
@cache.memoize(300)
def article_all():
    docs = ViewAll()
    return docs.show()

@app.route('/api', methods=["POST"])
def use_api():
    return api.main_wsgi(request)


@app.route('/writecomment', methods=["POST"])
def write_comment():

    return addComment_wsgi(request)


@app.route('/job/page/<page_num>')
@cache.memoize(300)
def ppfjob_page(page_num):
    orms = Jobs()
    return job_page(orms, page_num)

@app.route('/jobsearch/page/<page_num>')
@cache.memoize(300)
def ppfjobsearch_page():
    orms = Jobsearches()
    pass

@app.route('ppfjobsearches')
def ppfjobsearchs():
    pass

@app.route('/ppfjobs')
@cache.memoize(300)
def ppfjobs():
    orms = Jobs()
    return jobs_filtered(orms)


def _checkArticleIndex(err_msg):
    msg = str(err_msg)
    if msg.find(config.index_file) == -1:
        return False
    return True

@app.errorhandler(InitError)
def handle_init_error(error):
    from ppf import install
    return install.main()

@app.errorhandler(PageNotFound)
def handle_PageNotFound(error):
    from flask import jsonify
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

if __name__ == '__main__':
    config.PPFJOB_LOCAL_MODE = True
    app.run(port=3109)
