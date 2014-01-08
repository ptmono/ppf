from dnews.scraper		import Scraper
from dScrapper.reporter	import SaraminIt
from dScrapper.container.saramin import SaraminItModel

class Orms(object):
    __scraper = None
    def __new__(cls, *args, **kwargs):
        if not cls.__scraper:
            scraper = Scraper(SaraminItModel, "sqlite:////home/ptmono/myscript/0services/dScrapper/dScrapper/dbs/SaraminIt.sqlite")    
            orms = scraper.session.query(scraper.mapped_class).all()
            orms.reverse()
            cls.__scraper = orms
        return cls.__scraper
