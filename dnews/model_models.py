import time

from cgi import parse_qs

import requests

try:
    from urlparse import urlparse
    from urllib import unquote
except ImportError:
    from urllib.parse import urlparse
    from urllib.parse import unquote
    

from lxml.cssselect import CSSSelector
from lxml.html import parse, fromstring, tostring

from .model import GetSetModel
from .model_tools import CssParsers

from dlibs.logger import logger

class DaumCafe(GetSetModel, CssParsers):
    """
    To scrap daum cafe we have to notice two things.
     - cafe has request limitation. 50 requests / 1 minute

     - I think that he uses some technique to protect the content of
       cafe. The content is wrapped xmp tag. The strange thing is I
       couln't parse the content wrapped xmp tag with lxml and
       beautifulsoup. To solve this problem I renamed the xmp tag to div
       tag.

    >>> sample = '/home/ptmono/tmp/newstapa/daum_cafe_mbc_anti/test.html'
    >>> fd = open(sample, 'r')
    >>> data = fd.read()
    >>> fd.close()

    >>> #dc = DaumCafe()
    >>> #dc.get(data)
    >>> #dc.getContent()
    >>> #dc.title_urls
    >>> #len(dc.title_urls) # 24
    >>> #len(dc.getTitle()) # 24

    """
    def _parse(self, selector):
        result = []
        sel = CSSSelector(selector)
        sel_list = sel(fromstring(self.source))
        for sel in sel_list:
            title = sel.text_content()
            result.append(title)
        return result
        
    
    def setTitle_urls(self):
        result = []
        url_base = "http://cafe441.daum.net"
        selector = ('table[class="bbsList"] tr td[class="subject"] a')
        sel = CSSSelector(selector)
        sel_list = sel(fromstring(self.source))
        for sel in sel_list:
            url = url_base + sel.get('href')
            result.append(url)
        return result
    
    def Test(self):
        selector = ('table[class="bbsList"] tr td[class="date"]')
        sel = CSSSelector(selector)
        sel_list = sel(fromstring(self.source))
        print(sel_list[0].text_content())

    def getUrl(self):
        return self.title_urls
    
    def getTitle(self):
        return self.all_content(self.source, 'table[class="bbsList"] tr td[class="subject"] a')

    def getWriter(self):
        return self.all_content(self.source, 'table[class="bbsList"] tr td[class="nick"] a')

    def getDate(self):
        return self.all_content(self.source, 'table[class="bbsList"] tr td[class="date"]')

    def getContent(self):

        result = []
        request_count = 0
        # Daum has request limitation 50 requests per 1 min.
        save_count = 0
        count_base = 48
        count = count_base
        delay = 62
        for url in self.title_urls:

            print("aaa: " + url)
            try:
                data = requests.get(url).content
            #LocationParseError: Failed to parse: Failed to parse: cafe441.daum.netjavascript:;
            except Exception:
                try:
                    data = requests.get(url).content
                except:
                    result.append("")
                    logger().error(url)
                    count -= 1
                    continue

            try:
                # xmp tag contains the content. But I couldn't parse with
                # either lxml and beautifulsoup. _parse_first_text2 shows
                # my method. I changed xmp to div.
                content = self._parse_first_text2(data, 'div[id="template_xmp"]')
            except:
                msg = "content error: ", url
                logger().error(msg)
                content = ""
            result.append(content)

            if not count:
                count = count_base
                time.sleep(delay)
            count -= 1
            request_count += 1
            print("request_count: " + request_count)

        return result

    def _parse_first_text(self, data, selector):
        selector = (selector)
        sel = CSSSelector(selector)
        sel_list = sel(fromstring(data))
        content = sel_list[0].text_content()
        return content

    def _parse_first_text2(self, data, selector):
        data = data.replace("<xmp id", "<div id")
        data = data.replace("</xmp>", "</div>")

        selector = (selector)
        sel = CSSSelector(selector)
        sel_list = sel(fromstring(data))
        content = sel_list[0].text_content()

        return content

class DaumCafeContent(GetSetModel):
    """
    >>> sample = '/home/ptmono/tmp/newstapa/daum_cafe_mbc_anti/cafe_content_sample3.html'
    >>> fd = open(sample, 'r')
    >>> data = fd.read()
    >>> fd.close()

    >>> #dc = DaumCafeContent()
    >>> #dc.get(data)
    >>> #dc.getTest()
    """
    urls = ['/home/ptmono/tmp/newstapa/daum_cafe_mbc_anti/cafe_content_sample3.html']
    def getTest(self):
        #selector = ('table[class="protectTable"] td')
        selector = ('xmp[id="template_xmp"]')        
        sel = CSSSelector(selector)
        sel_list = sel(fromstring(self.source))
        #print tostring(sel_list[0])
        print(sel_list[0].text_content())

    



### === Etcs
### ______________________________________________________________
def get_contentval(url):
    """
    >>> url = "http://cafe441.daum.net/_c21_/bbs_read?grpid=1GeT3&mgrpid=&fldid=7vQ1&page=1&prev_page=0&firstbbsdepth=001CHzzzzzzzzzzzzzzzzzzzzzzzzz&lastbbsdepth=zzzzzzzzzzzzzzzzzzzzzzzzzzzzzz&contentval=000fBzzzzzzzzzzzzzzzzzzzzzzzzz&datanum=2553&listnum=10000"
    >>> get_contentval(url)
    '000fBzzzzzzzzzzzzzzzzzzzzzzzzz'
    
    """
    _, _, _, purl = parseURL(url)
    return purl['contentval']

def public_url(url):
    contentval = get_contentval(url)
    purl = "http://cafe441.daum.net/_c21_/bbs_search_read?grpid=1GeT3&fldid=7vQ1&contentval=%s&nenc=&fenc=&q=&nil_profile=cafetop&nil_menu=sch_updw" % contentval
    return purl


def download_titles():
    # listnum is work, So we can get 10000 news
    url = "http://cafe441.daum.net/_c21_/bbs_list?grpid=1GeT3&mgrpid=&fldid=7vQ1&firstbbsdepth=001CHzzzzzzzzzzzzzzzzzzzzzzzzz&lastbbsdepth=001Bxzzzzzzzzzzzzzzzzzzzzzzzzz&prev_page=2&page=1&listnum=10000&sortType="
    data = requests.get(url).content
    fd = open("daum_yourmbc_1_4628.html", 'w')
    fd.write(data)
    fd.close()

        
def get_sample(url, name):
    """
    >>> name = 'cafe_content_sample3.html'
    >>> url = 'http://cafe441.daum.net/_c21_/bbs_read?grpid=1GeT3&mgrpid=&fldid=7vbk&page=1&prev_page=0&firstbbsdepth=001CHzzzzzzzzzzzzzzzzzzzzzzzzz&lastbbsdepth=zzzzzzzzzzzzzzzzzzzzzzzzzzzzzz&contentval=&datanum=191&listnum=10000&searchlist_uri=&search_ctx='

    >>> get_sample(url, name) #doctest: +SKIP

    >>> name = 'cafe_content_sample2553.html'
    >>> url = 'http://cafe441.daum.net/_c21_/bbs_read?grpid=1GeT3&mgrpid=&fldid=7vQ1&page=1&prev_page=0&firstbbsdepth=001CHzzzzzzzzzzzzzzzzzzzzzzzzz&lastbbsdepth=zzzzzzzzzzzzzzzzzzzzzzzzzzzzzz&contentval=000fBzzzzzzzzzzzzzzzzzzzzzzzzz&datanum=2553&listnum=10000'

    >>> get_sample(url, name) #doctest: +SKIP
    
    """
    data = requests.get(url).content
    fd = open(name, 'w')
    fd.write(data)
    fd.close()


    
