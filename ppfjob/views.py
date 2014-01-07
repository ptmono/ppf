#!/usr/bin/env python
# coding: utf-8

from django.http import HttpResponse
from django.core.paginator import Paginator

from django.conf import settings

from jinja2 import FileSystemLoader, Environment, Markup

try:
    settings.configure()
except RuntimeError:
    pass
from django.shortcuts import render_to_response

from dnews.scraper		import Scraper
from dScrapper.reporter	import SaraminIt
from dScrapper.container.saramin import SaraminItModel

from .sentence	import is_spam, is_near

from dlibs.logger import loggero
from dlibs.common import *

from ppf import config as ppfconfig
PPF_MEDIA = ppfconfig.medias_d

settings.TEMPLATE_DIRS = (
    PPF_MEDIA,
)



template_dirs = getattr(settings, 'TEMPLATE_DIRS')
#default_mimetype = gettattr(settings, 'DEFAULT_CONTENT_TYPE')
env = Environment(loader=FileSystemLoader(template_dirs))

def jinja_render_to_response(filename, context={}):#, mimetype=default_mimetype):
    def sanitize_html(text):
        return Markup(scrubber.Scrubber(remove_comments=False).scrub(text))
    env.filters['sanitize_html'] = sanitize_html
    if ppfconfig.PPFJOB_LOCAL_MODE:
        from .sentence import is_spam, is_near
    else:
        def is_spam(aa): return False
        def is_near(text):
            regions = [u('부산'), u('창원'), u('마산'), u('경남'), u('울산')]
            if word_counter(text, regions, 2, 2):
                return True
            return False
        env.globals['is_spam'] = is_spam
        env.globals['is_near'] = is_near

    template = env.get_template(filename)
    rendered = template.render(**context)
    return rendered


def getJobs(page):
    reporter = SaraminIt()
    scraper = Scraper(SaraminItModel, "sqlite:////home/ptmono/myscript/0services/dScrapper/dScrapper/dbs/SaraminIt.sqlite")

    orms = scraper.session.query(scraper.mapped_class).all()
    orms.reverse()

    paginator = Paginator(orms, 30)

    if not page:
        page = 1

    page = paginator.page(page)
        
    return page.object_list

def job_page(page=None):

    mm = getJobs(page)
    return jinja_render_to_response('content_page_request.html', dict(articles=mm))

def jobs_filtered(page=None):
    mm = getJobs(page)

    return jinja_render_to_response('jinja_content_job.html', dict(articles=mm))

