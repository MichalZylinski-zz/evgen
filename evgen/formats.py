from builtins import str
from builtins import object
from copy import copy
import abc
import json
from future.utils import with_metaclass

class GenericEventFormat(with_metaclass(abc.ABCMeta, object)):
    """
    GenericEventFormat class is basis for all formatters. 
    """
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
            v = [str(attrs.get(f, ""), encode="utf-8") for f in self.Fields]
        else:
            v = [str(a, encode='utf-8') for a in attrs.values()]
        if self.Quote:
            v = [self.Quote+i.replace(self.Quote, "\\"+self.Quote)+self.Quote for i in v]
        return self.Separator.join(v)

class JSONEventFormat(GenericEventFormat):
    def format(self, attrs):
        if self.Fields:
            return json.dumps({f: str(attrs[f]) for f in self.Fields})
        else:
            return json.dumps({a:str(attrs[a]) for a in attrs})




