import sys
from common import *

from scraper import Scraper

from dlibs.logger import logger, loggero

import logging
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

import requests

class NateBreakingNewsModel2(GetSetModel):
    url_format = "http://news.nate.com/recent?mid=n0100&type=c&date=%s&page=%s"
    #url_range = [[20130623], [range(1, 200)]]
    url_range = [[20130621], [range(1, 3001)]]

    def set_sels(self):
        selector = ('dl[class="mduSubjectContent"]')
        sel = CSSSelector(selector)
        sel_list = sel(fromstring(self.source))
        return sel_list
        
    def getTitle(self):
        result = []
        selector = ('a strong')
        sel_sub = CSSSelector(selector)
        for sel in self._sels:
            sel_list = sel_sub(sel)
            title = sel_list[0].text_content()
            result.append(title)
        return result

    def getSummary(self):
        result = []
        selector = ('dd a')
        sel_sub = CSSSelector(selector)
        for sel in self._sels:
            sel_list = sel_sub(sel)
            try:
                summary = sel_list[0].text_content().strip()
            except IndexError as err:
                logger().debug(sel_list)
                summary = ""
            result.append(summary)
        return result
    
    def getUrl(self):
        result = []
        selector = ('a')
        sel_sub = CSSSelector(selector)
        for sel in self._sels:
            sel_list = sel_sub(sel)
            result.append(sel_list[0].get('href'))
        return result

    def getMedia(self):
        result = []
        selector = ('span[class="medium"]')
        sel_sub = CSSSelector(selector)
        for sel in self._sels:
            sel_list = sel_sub(sel)
            try:
                media = sel_list[0].text.strip()
            except IndexError as err:
                logger().debug(sel_list)
                media = ""
            result.append(media)
        return result

    def getContent(self):
        return ['' for i in range(len(self._sels))]


#Obsolete: This function is not work correctly. Current the way how to find
#the latest page uses lxml. So I stop the coding. Use latest_page
def detect_latest_page(date):
    """
    >>> #date = 13080408
    >>> #detect_latest_page(date)

    >>> #len of start page is 131652
    >>> #len of end page is 118667
    >>> #difference 12993

    >>> #detect_latest_page(13080316)
    """
    url_format = "http://news.nate.com/recent?mid=n0100&type=c&date=%s&page=%s" 
    
    def isEmptyPage(start_gab, cur_gab):
        """
        @start_gab: default gab between the length of full content and
        the length empty content

        @ cur_gab: gab between the length of full content and current content
        
        """
        gab = abs(start_gab - cur_gab)
        # This doesn't detect 2~3 article
        if gab < (start_gab * 0.3):
            return True
        return False

    def kk(page, page_gab, start_gab, start_clen, date, direction=-1, min_page_gab=50):
        count = 0
        while True:
            if page_gab < min_page_gab: return page
            if direction < 0:
                page -= page_gab
            else:
                page += page_gab

            url = url_format % (page, date)
            loggero().debug("Detecting page %s" % page)
            clen = len(requests.get(url).content)
            cur_gab = start_clen - clen
            if isEmptyPage(start_gab, cur_gab):
                direction = -1
            else:
                direction = 1
            page_gab = page_gab/2
                

    page_gab = 250
    aa = range(1000, 4000, 500)

    start_url = url_format  % (date, 1)
    loggero().debug(start_url)
    start_clen = len(requests.get(start_url).content)

    end_url = url_format % (date, 6000)
    end_clen = len(requests.get(end_url).content)

    start_gab = start_clen - end_clen

    for a in aa:
        url = url_format % (date, a)
        clen = len(requests.get(url).content)
        breakpoint = a

        cur_gab = start_clen - clen
        if isEmptyPage(start_gab, cur_gab): break

    # Current breakpoint is empty page.
    return kk(breakpoint, page_gab, start_gab, start_clen, date)


def latest_page(date):
    """
    >>> latest_page(20130723)
    1590
        
    """
    url_format = "http://news.nate.com/recent?mid=n0100&type=c&date=%s&page=%s"
    url = url_format % (date, 6000)
    content = requests.get(url).content

    selector = ('div[id="newsContents"] span[class="page"] a')
    sel = CSSSelector(selector)
    sel_list = sel(fromstring(content))
    return int(sel_list[-1:][0].text_content())

#Obsolete. Use get_range and get_dbname
def ran_and_db(t):
    """

    >>> len(ran_and_db(13080302))
    2
    
    """
    ran = [[t], [range(1, 3001)]]
    filename = "sqlite:///nate/natebreaking" + str(t) + ".sqlite"
    
    return (ran, filename)

def get_range(date):
    lspage = latest_page(date)
    # We scrap to lspage
    return [[date], [range(1, lspage+1)]]

def get_dbname(date):
    return "sqlite:///nate/natebreaking" + str(date) + ".sqlite"

def scrap(date, thread=None):

    url_range = get_range(date)
    dbname = get_dbname(date)
    smodel = NateBreakingNewsModel2()
    smodel.url_range = url_range
    scraper = Scraper(smodel, dbname, thread=thread)
    try:
        scraper.dododo()
    except Exception as err:
        logger.info("End %s" % date)
        sys.exit(0)

def main():
    
    url = "http://news.nate.com/recent?mid=n0100&type=c&date=20130625&page=1700"

    for i in range(20130602, 20130631):
        url_range, filename = ran_and_db(i)

        smodel = NateBreakingNewsModel2()
        smodel.url_range = url_range
        scraper = Scraper(smodel, filename)
        try:
            scraper.dododo()
        except Exception as err:
            if str(err) == 'This seems the end.':
                continue
            else:
                print("ERROR %s" % i)

if __name__ == "__main__":
    #main()
    scrap(20130803)
