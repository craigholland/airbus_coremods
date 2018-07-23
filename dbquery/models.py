from datetime import datetime as dt
from protorpc import messages
import enum
from google.appengine.api import memcache
from google.appengine.ext import ndb
from pyramid.response import Response

from _base.common import common_models

class Model(object):
    """All Models."""

    def add(self, model):
        if isinstance(model, common_models.BaseModel):
            self.__setattr__(model.__name__, model)

AllModels = Model()