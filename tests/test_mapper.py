from common import *
from unittest import TestCase

from dnews.mapper import ModelMapper, MapperClass, metadata

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker


class Test_NateBreaking(TestCase):
    def basic(self):
        nate_model = NateBreakingNewsModel()
        self.assertEqual(list(vars(NateBreakingNewsModel)), 627)


def in_design_attrs(model):
    for attr in dir(model):
        if not attr[0] == "_":
            return True
        return False

class Test_ModelMapper(TestCase):
    def test_remove_design_atts(self):
        mapper = ModelMapper(DummyModel)
        result = mapper._remove_design_attrs(mapper._model)
        self.assertEqual(in_design_attrs(result), False)

    def test_mapping(self):
        mapper = ModelMapper(DummyModel)
        mapper2 = ModelMapper(DummyModel)
        
        #self.assertEqual(mapper._model._info['columns'], {'url': 'getUrl', 'media': 'getMedia', 'title': 'getTitle', 'summary': 'getSummary'})

        self.assertEqual(mapper._model._info['columns'],
                         {'url': 'getUrl', 'num': 'getNum', 'title': 'getTitle'})


        self.assertEqual(mapper.object().__class__.__name__, 'type')
        self.assertEqual(mapper.object().__name__, 'DummyModel')
        self.assertTrue(isinstance(type(mapper.object()), type))
        
        #self.assertEqual(type(mapper.mapper()).__name__, 'Mapper')

        obj = mapper.mapper()

        nate = obj()

        nate.title = "tttile"
        nate.url = "http://nate.com"
        nate.aaa = "fff"

        engine = create_engine('sqlite:///:memory:', echo=False)
        # create table
        metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(nate)
        session.commit()

        self.assertEqual(obj.__name__, 'MapperClass')
        one = session.query(obj).filter_by(title='tttile').one()
        self.assertEqual(one.url, 'http://nate.com')

        from sqlalchemy import exc
        # Table NateBreakingNewsModel is already defined for this MetaData
        self.assertRaises(exc.InvalidRequestError, mapper.mapper)

        nate2 = MapperClass()
        nate2.title = "title2"
        nate2.url = "http://nate.com2"

        session.commit()


