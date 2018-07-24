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

    def add(self, model):
        if inspect.isclass(model) and issubclass(model, common_models.BaseModel):
            self.__setattr__(model.__name__, model)
            return model.__name__
        else:
            return 'Fail {0}'.format(model.__name__)

    def list_all_models(self):
        models = []
        for x in [y for y in dir(self) if not y.startswith('_') and inspect.isclass(y)]:
            models.append(x.__name__)
        return models

    def get_model_by_name(self, name):
        for x in [y for y in dir(self) if not y.startswith('_') and inspect.isclass(y)]:
            if x.__name__ == name:
                return x
        return None


AllModels = Model()