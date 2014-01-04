#!/usr/bin/python
# coding: utf-8

from dnews.smodel.common import *
import re
from lxml import etree

cur_file_path = os.path.abspath(__file__)
cur_dir_path = os.path.dirname(cur_file_path)


"""

http://www.saramin.co.kr/zf_user/upjikjong-recruit/upjikjong-list/pageCount/0/categoryCode/9%7C4/order/RD/category_level/top/recruitform_type/classified/tcode/9/mcode/9/bcode/4/page/2

http://www.saramin.co.kr/zf_user/upjikjong-recruit/upjikjong-list/pageCount/0/categoryCode/9%7C4/category_level/top/page/1

http://www.saramin.co.kr/zf_user/upjikjong-recruit/upjikjong-list/categoryCode/9%7C4/category_level/top/recruitform_type/classified/tcode/9/mcode/9/bcode/4/parent_level/top/arrayOrder/empty/list/search/order/RD

queries
=======

 - pageCount/1000: count of titles
 - order/RD : 최근 등록일 순으로 정렬
 - page/2


information
===========

 - 보통 8,000 10,000 정도의 구인 정보가 있습니다.


"""

class SaraminIt(GetSetModel, CssParsers):
    #urls = ['/home/ptmono/works/job/daum_cafe_job/datas/saramin1000.html']
    #urls = ['/home/ptmono/works/job/saramin/datas/saramin130701_1.html',
    #        '/home/ptmono/works/job/saramin/datas/saramin130701_2.html']

    def init_get(self):
        self.etree = etree.HTML(self.source)
        #self.etree_joblist = self.etree.xpath('//div[@id="jobs_list"]//tr[@id contains("rec")]')
        self.etree_joblist = self.etree.xpath('//div[@id="jobs_list"]')[1]
        #self.etree_sums = self.etree.xpath('//div[@id="jobs_list"][1]//tr[@class="position-detail"]')
        
    def set_range(self):
        selector = 'tr[id*="rec-"] p[class="corp-tit"] a span'
        self.titles = self.css_all_content(self.etree_joblist, selector)
        return len(self.titles)

    def getTitle(self):
        return self.titles

    def getCorpname(self):
        selector = 'tr[id*="rec-"] div[class="company_name"] span'
        return self.css_all_content(self.etree_joblist, selector, removetabs=True)

    def getDate(self):
        selector = 'tr[id*="rec-"] td:nth-of-type(5)'
        return self.css_all_content(self.etree_joblist, selector, removetabs=True)

    def getCount(self):
        selector = 'tr[id*="rec-"] td:nth-of-type(6)'
        return self.css_all_content(self.etree_joblist, selector, removetabs=True)

    def getDate_late(self):
        return [None] * self._range

    def getIdx(self):
        result = []
        selector = 'tr[id*="rec-"] a[id*="rec_link_"]'        
        sel = CSSSelector(selector)
        sel_list = sel(self.etree_joblist)
        for sel in sel_list:
            idx = sel.get('href')
            try:
                idx = re.match(".*idx=([0-9]*).*", idx).group(1)
            except:
                idx = ""
            result.append(idx)
        return result

    def getContent(self):
        return [""] * self._range

    def getCorpidx(self):
        result = []
        sel_list = self.etree.xpath('//div[@class="company_name"]')
        for s in sel_list:
            try:            
                ahref = s.xpath("a")[0].get('href')
                cidx = re.search('idx/([0-9]+)', ahref).group(1)
                result.append(cidx)
            except Exception as err:
                result.append("")
            
        return result


    def getBody(self):
        """
        How about to get full body. It seems 'div[id="divPrintArea"]'

        """
        return [""] * self._range

    def getCity(self):
        """
        """
        # selector = 'ul li span:nth-child(1)'
        # return self.css_all_content(self.etree_joblist, selector)

        # If emplyer doesn't write cith, then it will loss the city. So we
        # will get only 499 on 500.
        result = []
        xpath_region = '//div[@class="corp-con hs_corp"]//li//span[1]'
        sel_list = self.etree_joblist.xpath(xpath_region)
        for sel in sel_list:
            try:
                result.append(sel.text)
            except:
                # Index error will be occured when no region
                result.append('')
        return result

        

    def getMoney(self):
        return [""] * self._range

    def getPriority(self):
        """
        we can exclude "고용촉진장려금 대상"
        """
        return [""] * self._range

    def getCorp_employ_num(self):
        """
        Number of employees
        """
        return [""] * self._range

    def getSubmit_num(self):
        """
        지원자 수
        """
        return [""] * self._range

    def getSpam(self):
        return [""] * self._range


class SaraminItSearch(GetSetModel, CssParsers):

    def init_get(self):
        self.etree = etree.HTML(self.source)
        self.etree_joblist = self.etree.xpath('//ul[@class="type02"]')[0]
    
    def getCorpname(self):
        xpath = '//li[@class="list"]//dl//dt//span'
        return self.xpath_all_content(self.etree_joblist, xpath)

    def getTitle(self):
        xpath = '//dd[@class="txt-inline"]//a[1]'
        result = []
        sel_list = self.etree_joblist.xpath(xpath)
        for s in sel_list:
            data = s.get('title')
            result.append(data)
        return result


    def getIdx(self):
        xpath = '//dd[@class="txt-inline"]//a[1]'
        result = []
        sel_list = self.etree_joblist.xpath(xpath)
        for s in sel_list:
            data = s.get('href')
            try:
                idx = re.match(".*idx=([0-9]*).*", data).group(1)
            except:
                idx = ''
            result.append(idx)
        return result
        

class SaraminItTest(GetSetModel, CssParsers):
    """
    >>> #url = 'http://www.saramin.co.kr/zf_user/upjikjong-recruit/upjikjong-list/pageCount/0/categoryCode/9%7C4/category_level/top/page/2/order/RD'
    >>> #NetTools.save_page(url, _dummy_path)
        
    >>> #data = SaraminItTest._dummy_data()
    
    >>> #obj = SaraminItTest()
    >>> #info = obj.get(data)
    >>> #len(info['corpidx'])
    30
    >>> #obj.getCorpidx()

    """
    urls = ['/home/ptmono/works/job/saramin/datas/saramin130701_1.html',
            '/home/ptmono/works/job/saramin/datas/saramin130701_2.html']
    dummy_path = os.path.join(cur_dir_path, '__tmp/saramin_it_sample.html')

    @classmethod
    def _dummy_data(self):
        return NetTools.read(self.dummy_path)
        
    def getCorpidx(self):
        result = []
        # selector = 'div[class="company_name"]'
        # sel = CSSSelector(selector)
        # sel_list = sel(fromstring(self.source))
        
        tree = etree.HTML(self.source)
        #xpath = '//td[@class="welfare_detail"]'
        #xpath = 'div[id="jobs_list"] tr[id*="rec-"] p[class="corp-tit"]'
        xpath = '//div[@class="company_name"]//span'
        sel_list = tree.xpath(xpath)
        for s in sel_list:
            try:            
                cidx = s.text
                result.append(cidx)
            except Exception as err:

                result.append("")
            
        return result


