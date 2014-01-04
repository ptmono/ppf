#!/usr/bin/python
# coding: utf-8

from dnews.smodel.common import *
from dnews.model_tools import CssParsers
from dnews.model_models import DaumCafe

class DaumCafeBreakjob(DaumCafe):
    urls = ['/home/ptmono/works/job/daum_cafe_job/datas/daum_cafe_breakjob_it18115.html']

    def getCount(self):
        return self.all_content(self.source, 'table[class="bbsList"] tr td[class="count"]')        
        
    def getContent(self):
        result = []
        for url in self.title_urls:
            result.append("")
        return result



class DaumCafeBreakjobSample(DaumCafe):
    urls = ['/home/ptmono/works/job/daum_cafe_job/datas/daum_cafe_breakjob_it_sample.html']

    def getCount(self):
        return self.all_content(self.source, 'table[class="bbsList"] tr td[class="count"]')        
        
    def getContent(self):
        result = []
        for url in self.title_urls:
            result.append("")
        return result


    
class DaumCafeBreakjobSampleContentTest(GetSetModel):
    """

    >>> dc = DaumCafeBreakjobSampleContentTest()
    >>> dc.get("")
    >>> dc.getContent()
    
    """
    urls = ['/home/ptmono/works/job/daum_cafe_job/datas/daum_cafe_breakjob_it_sample_parse_page.html']
    urls2 = ['/home/ptmono/works/job/daum_cafe_job/datas/mbcanti15.html']

    def getContent(self):
        fd = open(self.urls2[0], 'r')
        data = fd.read()
        fd.close()

        selector = 'div[id="template_xmp"]'
        data = data.replace("<xmp id", "<div id")
        data = data.replace("</xmp>", "</div>")

        selector = (selector)
        sel = CSSSelector(selector)
        sel_list = sel(fromstring(data))
        content = sel_list[0].text_content()
        
        return content

