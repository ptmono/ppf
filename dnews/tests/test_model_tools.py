
from common import *

from lxml import etree


class Test_CssParsers(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = NetTools.read(DummyModel.urls[0])
        cls.tree = etree.HTML(cls.data)

    def test_xpath_all_content(self):
        xpath = '//span[@class="mw_basic_list_num"]'
        self.assertEqual(CssParsers.xpath_all_content(self.tree, xpath)[0], '34659')
        
        model = DummyModel()
        info = model.get(self.data)
        #self.assertEqual(info, 7468)

    def test_remove_tabs(self):
        aa = '\r\n\t\t\t09/04 (수)'
        self.assertEqual(CssParsers.remove_tabs(aa), '09/04 (수)')
        

    def test_css_all_content(self):
        selector = 'span[class="mw_basic_list_num"]'
        CssParsers.css_all_content(self.data, selector)
        CssParsers.css_all_content(self.tree, selector)

        
        
