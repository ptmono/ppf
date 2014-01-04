
from sqlalchemy		import create_engine
from sqlalchemy.orm	import sessionmaker, scoped_session

from mapper import metadata, MapperClass, ModelMapper




class Session:
    def __init__(self, smodel, engine_name):
        pass
