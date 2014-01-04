#!/usr/bin/python
# coding: utf-8

from dnews.smodel.common import *

class NateBreakingNewsModel(GetSetModel):
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
#the latest page with lxml. So I stop the coding. Use latest_page
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
    
    def half(c): return c/2
    def half_plus(c): return c + c/2

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
    

def get_range(date):
    lspage = latest_page(date)
    # We scrap to lspage
    return [[date], [range(1, lspage+1)]]

def get_dbname(date):
    return "sqlite:///nate/natebreaking" + str(date) + ".sqlite"
