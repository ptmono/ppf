
from sqlalchemy import create_engine, MetaData

class GVar:
    metadata = MetaData()
    engine = create_engine('sqlite:///:memory:', echo=True)
