#!/usr/bin/python
# coding: utf-8

from common import *

from dnews.smodel.saramin	import SaraminIt, SaraminItTest
from dnews.scraper			import Scraper
from lxml import etree

dummy_path = os.path.join(SaraminItTest.dummy_path)

def get_sample(engine_name):
    url = "http://www.saramin.co.kr/zf_user/upjikjong-recruit/upjikjong-list/pageCount/500/categoryCode/9%7C4/category_level/top/page/1/order/RD"
    scraper = Scraper(SaraminIt, 'sqlite:///saramin_dummy.sqlite')
    scraper.urls = [url]
    scraper.dododo()
    

class Test_SaraminIt(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = NetTools.read(dummy_path)
        cls.tree = etree.HTML(cls.data)

        cls.model = SaraminIt()
        cls.model.get(cls.data)

    def test_basic(self):
        result = []
        xpath = '//div[@class="company_name"]//span'
        sel_list = self.tree.xpath(xpath)
        for s in sel_list:
            try:            
                cidx = s.text
                result.append(cidx)
            except Exception as err:

                result.append("")
        self.assertEqual(result[3], u('㈜디알에프앤'))
        self.assertEqual(len(result), 30)

    def test_joblsit(self):
        #self.assertEqual(self.model.etree_joblist, 3968)
        xpath_corname = '//div[@class="company_name"]//span'
        sel_list = self.model.etree_joblist.xpath(xpath_corname)
        self.assertEqual(len(sel_list), 30)

        self.assertEqual(CssParsers.xpath_all_content(self.model.etree_joblist, xpath_corname)[3],
                         u('㈜디알에프앤'))

        xpath_positions = '//tr[@class="position-detail"]'
        dates = CssParsers.xpath_all_content(self.model.etree_joblist, xpath_positions, True)
        self.assertEqual(len(dates), 30)


        # title with xpath
        xpath_title = '//span[@class="title-text"]'
        titles = CssParsers.xpath_all_content(self.model.etree_joblist, xpath_title)
        self.assertEqual(titles[3], u('㈜디알에프앤 | 증권HTS 컨텐츠 신입개발자 및 QA(QC) 모집'))
        self.assertEqual(len(titles), 30)

        # title with css
        selector_title = 'tr[id*="rec-"] p[class="corp-tit"] a span'
        stitles = CssParsers.css_all_content(self.model.etree_joblist,
                                               selector_title, removetabs=True)
        self.assertEqual(stitles[1], '연구개발직(신입/경력) 모집공고')
        self.assertEqual(len(stitles), 30)

        # region
        xpath_region = '//td[@class="area_detail"]//a[1]'
        region = CssParsers.xpath_all_content(self.model.etree_joblist, xpath_region)
        self.assertEqual(region[3], u('서울'))
        self.assertEqual(len(region), 30)

        # welfare
        xpath_welfare = '//td[@class="welfare_detail"]'
        welfare = CssParsers.xpath_all_content(self.model.etree_joblist, xpath_welfare)
        self.assertEqual(welfare[22],
                         '국민연금(4대보험), 고용보험(4대보험), 산재보험(4대보험), 건강보험(4대보험)')
        self.assertEqual(len(titles), 30)

        # date
        selector_date = 'tr[id*="rec-"] td:nth-of-type(5)'
        dates = CssParsers.css_all_content(self.model.etree_joblist, selector_date, removetabs=True)
        self.assertEqual(dates[3], '08/31 (토)')
        self.assertEqual(len(dates), 30)

        # count
        selector_count = 'tr[id*="rec-"] td:nth-of-type(6)'
        counts = CssParsers.css_all_content(self.model.etree_joblist, selector_count, removetabs=True)
        self.assertEqual(counts[3], '4')
        self.assertEqual(len(counts), 30)

        # corp_employ_num

        # money

        # corpname
        selector_corpname = 'tr[id*="rec-"] div[class="company_name"] span'
        corpnames = CssParsers.css_all_content(self.model.etree_joblist,
                                               selector_corpname, removetabs=True)
        self.assertEqual(corpnames[3], u('㈜디알에프앤'))
        self.assertEqual(len(corpnames), 30)


        
    def class_SaraminIt(self):
        aa = list(self.model.list(self.data))[1]
        expected = ('', u('경기 용인시'), '16362927', '', '', '', '88', '', '', '', u('고등기술연구원'), '08/16 (금)', u('연구개발직(신입/경력) 모집공고'), None, '')
        
        #self.assertEqual(aa, 333)
                            
        self.model.get(self.data)



class Test_SaraminIt2(TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    # Obsolete. We changed the xpath of city because saramin changed their
    # layout. So the sample 'saramin_error_sample1.html' is not right
    # sample.
    def error1(self):
        '''

        Total index is missed when no city. The employer empty the form
        of city.
        '''
    
        fd = open('saramin_error_sample1.html', 'rb')
        source = fd.read()
        fd.close()

        model = SaraminIt()
        infos = model.get(source)

        # the title missing the city form
        self.assertEqual((infos['title'][133], infos['city'][133]), (u('생생정보통신(주)KT 아파트 (IF)내선 공사 현장 기사 모집..'), u('')))

