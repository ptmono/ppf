#!/usr/bin/env python
# coding: utf-8

import sys
import os

from flask import Flask, request
from flask.ext.cache import Cache

app = Flask(__name__)
app.debug = True
cache = Cache(app, config={'CACHE_TYPE': 'null'})


from ppf import config
from ppf import api
from ppf.viewer import ViewHome, ViewId, ViewAll
from ppf.poster import addComment_wsgi
from ppf.app_exceptions import InitError, PageNotFound

from ppfjob.views import jobs_filtered, job_page
from ppfjob.models import Orms

from werkzeug import SharedDataMiddleware

from dnews.scraper		import Scraper
from dScraper.container.saramin import SaraminItModel

print(config.htmls_d)

app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/medias':	config.medias_d,
    '/files':	config.files_d
    })

def get_ppfjob_orms():
    scraper = Scraper(SaraminItModel, "sqlite:////home/ptmono/myscript/0services/dScraper/dScrapper/dbs/SaraminIt.sqlite")    
    orms = scraper.session.query(scraper.mapped_class).all()
    orms.reverse()
    return orms


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
@cache.memoize(3000)
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
@cache.memoize(3000)
def ppfjob_page(page_num):
    orms = Orms()
    return job_page(orms, page_num)

@app.route('/ppfjobs')
@cache.memoize(3000)
def ppfjobs():
    orms = Orms()
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
