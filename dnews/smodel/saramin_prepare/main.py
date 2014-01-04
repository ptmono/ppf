from dnews.smodel.common import *
from dnews.smodel.saramin import SaraminIt

from dnews.scraper import Scraper, MapperClass
from dnews.model_tools import NetTools


class SaraminItModel(GetSetModel, CssParsers):
    urls = ['http://www.saramin.co.kr/zf_user/search/jobs/page/2?pageCount=80&multiLine=&searchword=python&company_cd=1&area=&domestic=&oversee=&jobCategory=&jobType=&career=&order=&periodType=&period=&condition=&arange=&company=&employ=&rSearchword=&hSearchword=&hInclude=&hExcept=']

    dummy_path = os.path.join(
    @classmethod
    def _dummy_data(self):
        return NetTools.read(self.dummy_path)
    
    def init_get(self):
        self.etree = etree.HTML(self.source)
        #self.etree_joblist = self.etree.xpath('//div[@id="jobs_list"]//tr[@id contains("rec")]')
        self.etree_joblist = self.etree.xpath('//div[@id="jobs_list"]')[1]
        #self.etree_sums = self.etree.xpath('//div[@id="jobs_list"][1]//tr[@class="position-detail"]')
    

def main():
    #NetTools.save_page(SaraminItModel.urls[0], 'saramin_search.html')

    pass
    
    # orms = scraper.session.query(MapperClass).all()
    # for orm in orms:
    #     print(orm.title)
    #     print("\n")
    

# scraper = Scraper(SaraminItModel, "sqlite:///aa.sqlite")
# orms = scraper.session.query(MapperClass).all()
# for orm in orms:
#     print(orm.title)
#     print("\n")

# print(len(orms))

if __name__ == "__main__":
    main()
