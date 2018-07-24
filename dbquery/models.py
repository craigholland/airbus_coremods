from datetime import datetime as dt
from protorpc import messages
import enum
from google.appengine.api import memcache
from google.appengine.ext import ndb
from pyramid.response import Response
import inspect
from _base.common import common_models

class Model(object):
    """All Models."""


    def list_all_models(self):
        models = []
        for x in [y for y in dir(self) if not y.startswith('_') and inspect.isclass(y)]:
            models.append(x.__name__)
        return models

    def get_model_by_name(self, name):
        for y in dir(self):
            if y == name:
                return getattr(self, y)
        return None

def addToModel(model):
    if inspect.isclass(model) and issubclass(model, common_models.BaseModel):
        setattr(Model, model.__name__, model)
    return str(dir(Model))