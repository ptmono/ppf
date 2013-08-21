
from dnews.smodel.common import *

from lxml import etree

cur_file_path = os.path.abspath(__file__)
cur_dir_path = os.path.dirname(cur_file_path)

_dummy_path = os.path.join(cur_dir_path, '__tmp/torrentrg_movie.html')

class TorrentRgModel(GetSetModel, CssParsers):
    """
    >>> data = NetTools.read(TorrentRgModel.urls[0])
    
    >>> tr = TorrentRgModel()
    >>> dd = tr.get(data)
    >>> len(dd)
    3
    >>> len(dd['url'])
    30
    """
    urls = [_dummy_path]
    url_format = 'http://www.torrentrg.com/bbs/board.php?bo_table=torrent_movie&page=%s'

    def getNum(self):
        selector = 'span[class="mw_basic_list_num"]'
        result = CssParsers.css_all_content(self.source, selector)
        return result

    def getTitle(self):
        selector = 'td[class="mw_basic_list_subject"] a span'
        result = CssParsers.css_all_content(self.source, selector)
        leng = len(result)
        # Exclude notices
        start = leng - 30
        result = result[start:]
        return result

    def getUrl(self):
        result = []
        xpath = '//tr/td[@class="mw_basic_list_subject"]'
        tree = etree.HTML(self.source)
        elements = tree.xpath(xpath)

        start = len(elements) - 30
        for ele in elements[start:]:
            url = ele[2].get('href')
            url = url.replace('../', 'http://www.torrentrg.com/')
            result.append(url)

        return result
    


class TorrentRgTest(GetSetModel, CssParsers):
    """

    >>> #url = 'http://www.torrentrg.com/bbs/board.php?bo_table=torrent_movie'
    >>> #filename = '__tmp/torrentrg_movie.html'
    >>> #NetTools.save_page(url, filename)

    >>> tr = TorrentRgTest()
    >>> tr.getAa()
    33

    >>> tr.getBb()
    30
    """

    urls = [_dummy_path]

    def getAa(self):
        data = NetTools.read(self.urls[0])
        
        #selector = 'span[class="mw_basic_list_num"]' # 30 count
        selector = 'td[class="mw_basic_list_subject"] a span' # 30 count
        sel = CSSSelector(selector)
        sel_list = sel(fromstring(data))
        return len(list(sel_list))

    def getBb(self):
        data = NetTools.read(self.urls[0])

        # from StringIO import StringIO
        # data = StringIO(data)
        

        #from lxml import etree

        #tree = etree.parse(data)
        xpath = '//tr/td[@class="mw_basic_list_subject"]'
        #r = tree.xpath(xpath)

        # selector = 'td[class="mw_basic_list_subject"] a span' # 30 count
        # sel = CSSSelector(selector)
        # sel = CSSSelector(selector

        from lxml import etree
        tree = etree.HTML(data)
        #dir(tree.xpath(xpath)[0])
        trees = tree.xpath(xpath)
        start = len(trees) - 30
        result = []
        for tree in trees[start:]:
            url = tree[2].get('href')
            url = url.replace('../', 'http://www.torrentrg.com/')
            result.append(url)
        
        return len(result)

