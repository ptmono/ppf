#!/usr/bin/python
# coding: utf-8

from sqlalchemy import Table, Column, Integer, String, MetaData

class Container(object):
    """

    >>> container = Container(model)
    >>> # or
    >>> container = Container(db_file)

    >>> container.load()

    >>> container = Container(db_file)
    >>> 
    """

    def __init__(self, model):
        """

        We can get columns from model.
        """
        self.model = model

        # Inited with self.init
        self._session = None
        self.__obj = None

        self._init()

    def _init(self):
        if self.model:
            pass

    def _init_db(self):
        pass

    def _init_obj(self):
        if not self.model: return
        columns = self.model._info['columns'].keys()
        
        def create_table(name):
            return Table(name, metadata,
                    Column('id', Integer, primary_key=True))

            

class IteraterType(object):
    """
    It will inherted with Container class to specify the type of the
    container.
    
    """
        
class ContainerBaseStructure(object):
    def __init__(self, model):
        """
        model provides columns.
        """
        self.model = model

class ElementTypeBase(object):
    pass

class ObjectTypeBase(object):
    pass


class AtnBehavierMask(object):
    """
    Specify objec's behavier.
    """
    pass


class AtnInterface(object):
    """
    """

"""scribble:
    object --> 
"""
