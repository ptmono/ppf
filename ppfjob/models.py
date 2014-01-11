from dnews.scraper		import Scraper
from dnews.smodel.saramin	import SaraminIt
from dScraper.container.saramin import SaraminItModel

class Orms(object):
    __scraper = None
    def __new__(cls, *args, **kwargs):
        if not cls.__scraper:
            scraper = Scraper(SaraminItModel, "sqlite:////home/ptmono/myscript/0services/dScraper/dScraper/dbs/SaraminIt.sqlite")    
            orms = scraper.session.query(scraper.mapped_class).all()
            orms.reverse()
            cls.__scraper = orms
        return cls.__scraper
