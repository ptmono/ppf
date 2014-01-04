from common import *
from scraper import Scraper, MapperClass

scraper = Scraper(NateBreakingNewsModel2, "sqlite:///natebreaking3.sqlite")
orms = scraper.session.query(MapperClass).all()
# for orm in orms:
#     print(orm.title)
#     print("\n")

print(len(orms))

