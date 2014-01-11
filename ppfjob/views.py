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
from dnews.smodel.saramin	import SaraminIt
from dScraper.container.saramin import SaraminItModel

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
    template = env.get_template(filename)
    rendered = template.render(**context)
    return rendered

def getJobs(orms, page):
    paginator = Paginator(orms, 30)

    if not page:
        page = 1

    page = paginator.page(page)
        
    return page.object_list

def getJobs_first(orms):
    return orms[:30]
    
def job_page(orms, page=None):

    mm = getJobs(orms, page)
    return jinja_render_to_response('content_page_request.html', dict(articles=mm))

def jobs_filtered(orms):
    mm = getJobs_first(orms)
    return jinja_render_to_response('jinja_content_job.html', dict(articles=mm))

