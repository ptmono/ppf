#!/usr/bin/env python
# coding: utf-8

from django.http import HttpResponse
from django.core.paginator import Paginator

from django.conf import settings

from ppf.viewer import JinjaEnvironment

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
    return JinjaEnvironment().get_template('content_page_request.html').render(dict(articles=mm))

def jobs_filtered(orms):
    mm = getJobs_first(orms)
    return JinjaEnvironment().get_template('jinja_content_job.html').render(dict(articles=mm))

