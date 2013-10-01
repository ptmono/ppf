"""

metadata connect ModelMapper and engine. You can create engine

>>> engine = create_engine(engine_name, echo=False)

then create table

>>> metadata.create_all(engine)

Before create table, metadata have to know the table we want to create

>>> mapper = ModelMapper(smodel)
>>> mapper.mapper()

"""


from sqlalchemy		import Table, Column, Integer, String, MetaData, Unicode

from sqlalchemy		import MetaData
from sqlalchemy.orm import mapper, sessionmaker

from dlibs.logger	import loggero

metadata = MetaData()

class MapperClass(object): pass
    
class ModelMapper(object):
    """

    Map the model to the mapper of sqlalchemy. This class will create
    the datababase table of model.

    >>> mapper = ModelMapper(DummyModel)
    >>> mapped_cls = mapper.mapper()
    >>> dummy = MapperClass()
    """
    
    def __init__(self, model):
        if isinstance(model, type):
            self._model = model()
        else:
            self._model = model
        
    def _remove_design_attrs(self, model):
        if isinstance(model, type): du_model = model()
        else: du_model = model
        for attr in dir(model):
            if not attr[0] == "_":
                attr = getattr(du_model, attr)
                del attr
        return du_model

    def mapper(self, objcls=MapperClass, table=None):
        """
        Map OBJCLS and TABLE. This uses sqlalchemy.orm.mapper.

        Returns a mapped class. Default class is MapperClass. Default
        table is created by model.

        """
        if not table:
            table = self.table()
        loggero().debug(objcls)
        loggero().debug(type(objcls))
        mapper(objcls, table)
        
        return objcls

    def object(self):
        table_name = self._model.__class__.__name__
        # mapper requires the type object
        obj = type(table_name, (object,), {})
        return obj
        
    def table(self):
        table_name = self._model.__class__.__name__
        table = Table(table_name, metadata, Column('_id', Integer, primary_key=True),
                      *(Column(col, Unicode) for col in self._model._info['columns'].keys()),
                      extend_existing=True)
        return table


