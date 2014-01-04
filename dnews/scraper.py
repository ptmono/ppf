
from sqlalchemy		import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from dnews.mapper import metadata, MapperClass, ModelMapper
import threading
from collections import deque
        
import requests
from dlibs.logger import loggero

def parse(url, model):
    if url[:4] == 'http':
        source = requests.get(url).content
    else:
        fd = open(url, 'r')
        source = fd.read()
        fd.close()
    return model.get(source)


def split_list(lst,nb):
    """

    >>> bb = list(split_list(range(29), 4))
    >>> len(bb)
    4
    >>> bb = list(split_list(range(28), 4))
    >>> len(bb)
    4
    >>> bb = list(split_list(range(25), 10))
    >>> len(bb)
    10
    """
    
    # ln = length of smaller sublists 
    # extra = number of longer sublists (they have ln+1 items)
    lst = list(lst)
    ln,extra = divmod(len(lst),nb)
    pos = ln*(nb-extra) # position where larger sublists begin 
    return [ lst[i*ln:(i+1)*ln] for i in xrange(nb-extra) ]\
        + [lst[pos+i*(ln+1):pos+(i+1)*(ln+1)] for i in xrange(extra)] 


def divide_list(urls, sep):
    leng = len(urls)
    divider = leng/sep
    loggero().info(divider)
    loggero().debug(divider)
    for i in xrange(0, leng, divider):
        yield urls[i:i+divider]



class Scraper(object):
    """

    >>> #crawler = Scraper()

    >>> #crawler2 = Scraper(dbtype='sqlite3', model=sModel)
    >>> #crawler2.load()

    """

    def __init__(self, smodel, engine_name, mapped_class=None, thread=None):
        if mapped_class:
            self.mapped_class = mapped_class
        else:
            class MappedClass(object): pass
            self.mapped_class = MappedClass
        self.engine_name = engine_name
        #self.model = smodel()
        self.setModel(smodel)
        self.urls = self.model._info['urls']
        self.columns = self.model._info['columns'].keys()
        self.engine = None        
        self.session = None
        self.sessioncls = None
        self.thread = thread

        self._init()

    def _init(self):
        mapper = ModelMapper(self.model)
        mapper.mapper(self.mapped_class)
        self.engine = create_engine(self.engine_name, echo=False)

        # Create table
        # metadata is connected with mapper, MapperClass is mapped as object.
        metadata.create_all(self.engine)
        # self.sessioncls = sessionmaker(bind=self.engine)
        # self.session = self.sessioncls()
        self.sessioncls = sessionmaker(bind=self.engine, autoflush=True, autocommit=False)
        self.session = scoped_session(self.sessioncls)
        

    def setDb(self, db_name):
        self.db_name = db_name

    def setModel(self, model):
        if isinstance(model, type):
            self.model = model()
        else:
            self.model = model

    def dododo(self):
        if self.thread:
            self._dododo_thread()
        else:
            self._dododo_single()

    def _dododo_thread(self):

        pool = []
        # Split urls for each thread
        divided_urls = split_list(self.urls, self.thread)

        for i in range(self.thread):
            pool.append(Worker(self.session, self.model, self.mapped_class, divided_urls[i]))
        loggero().debug(pool)
            
        for thread in pool:
            thread.start()

        for thread in pool:
            thread.join()
        
            
    def _dododo_single(self):
        for url in self.urls:
            data = parse(url, self.model)
            loggero().info(url)
            self._save(data)


    def _save(self, info):
        """

        INFO has a form {'col1': ['i1', 'i2', 'i3'], 'col2': ['j1', 'j2', 'j3']}.

        """
        cols = info.keys()
        zipped_cols = zip(*(info[col] for col in info))
        zipped_cols_count = len(list(zipped_cols))
        loggero().debug(zipped_cols_count)
        if zipped_cols_count == 0:
            raise Exception("This seems the end.")

        for element in zipped_cols:
            count = 0
            # TODO: Using orm is slow method. But easy.
            orm = self.mapped_class()
            for col in cols:
                setattr(orm, col, element[count])
                count += 1
            self.session.add(orm)

        self.session.commit()

class Worker(threading.Thread):
    def __init__(self, session, model, mapper, urls):
        super(Worker, self).__init__()
        self.session = session
        self.model = model
        self.mapper = mapper
        self.urls = urls

    def run(self):
        for url in self.urls:
            data = parse(url, self.model)
            loggero().info(url)
            self._save(data)

    def _save(self, info):
        """

        INFO has a form {'col1': ['i1', 'i2', 'i3'], 'col2': ['j1', 'j2', 'j3']}.
        """
        cols = info.keys()
        zipped_cols = zip(*(info[col] for col in info))
        zipped_cols_count = len(zipped_cols)
        loggero().debug(zipped_cols_count)
        if zipped_cols_count == 0:
            raise Exception("This seems the end.")

        for element in zipped_cols:
            count = 0
            # TODO: To use orm is slow method. But easy.
            orm = self.mapper()
            for col in cols:
                setattr(orm, col, element[count])
                count += 1
            self.session.add(orm)

        self.session.commit()
            
        
class Worker2(threading.Thread):
    def __init__(self, sessioncls, queue, model):
        self.session = sessioncls()
        self.model = model
        self.queue = queue

    def run(self):
        is_queue = True
        url = None
        while is_queue:
            try:
                url = self.queue.pop()
            except IndexError as err:
                break

            data = parse(url, self.model)
            loggero().info(url)
            self._save(data)
    
    def _save(self, info):
        """

        INFO has a form {'col1': ['i1', 'i2', 'i3'], 'col2': ['j1', 'j2', 'j3']}.
        """
        cols = info.keys()
        zipped_cols = zip(*(info[col] for col in info))
        zipped_cols_count = len(zipped_cols)
        loggero().debug(zipped_cols_count)
        if zipped_cols_count == 0:
            raise Exception("This seems the end.")

        for element in zipped_cols:
            count = 0
            # TODO: To use orm is slow method. But easy.
            orm = MapperClass()
            for col in cols:
                setattr(orm, col, element[count])
                count += 1
            self.session.add(orm)

        self.session.commit()

