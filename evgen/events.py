from builtins import map
from builtins import str
from builtins import object
import abc
import json
from future.utils import with_metaclass

class GenericEventFormat(with_metaclass(abc.ABCMeta, object)):
    def __init__(self, fields=None):
        self.Fields = fields

    @abc.abstractmethod
    def format(self, attrs):
        pass

class CSVEventFormat(GenericEventFormat):
    def __init__(self, fields=None, sep=",", quote=""):
        self.Separator = sep
        self.Quote=quote
        self.Fields = fields

    def format(self, attrs):
        if self.Fields:
            v = list(map(str, [attrs[f] for f in self.Fields]))
        else:
            v = list(map(str, list(attrs.values())))
        if self.Quote:
            v = [self.Quote+i.replace(self.Quote, "\\"+self.Quote)+self.Quote for i in v]
        return self.Separator.join(v)

class JSONEventFormat(GenericEventFormat):
    def format(self, attrs):
        if self.Fields:
            return json.dumps({f: str(attrs[f]) for f in self.Fields})
        else:
            return json.dumps({a:str(attrs[a]) for a in attrs})


class GenericEventTemplate(object):
    def __init__(self, name=None, writer=None, **kwargs):
        self.Name = name
        self.__dict__.update(kwargs)
        self.__writers__ = []
        self.__has_writer__ = False
        if writer!= None:
            self.add_writer(writer)

    def has_writer(self):
        return self.__has_writer__

    def add_writer(self, writer,  replace=False):
        if replace:
            self.__writers__ = []
        self.__writers__.append(writer)
        self.__has_writer__ = True

    def preprocess(self):
        pass

    def generate(self):
        if len(self.__writers__) == 0:
            raise ValueError("Writer property missing.")
        self.preprocess()
        attrs = {a:self.__dict__[a] for a in self.__dict__ if not a.startswith("_") and self.__dict__[a] is not None}
        for c in self.__writers__:
            c.send(attrs)


class EventGroup(object):
    def __init__(self):
        self.events = []
        self.min_repeat = 1
        self.max_repeat  = 1

    def add_event(self, event, probability, delay=1000, delay_random=0.1):
        self.events.append((event, probability, delay, delay_random))

    def set_repeat_policy(self, min=1, max=1):
        self.min_repeat = min
        self.max_repeat = max



