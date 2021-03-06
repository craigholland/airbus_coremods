import protorpc
from datetime import datetime as dt

from google.appengine.ext import ndb
from _base.common import common_models

class RegisteredServices(common_models.BaseModel):
    service_name = ndb.StringProperty()

class API_Registry(common_models.BaseModel):
    RegisteredServices__key_name = ndb.StringProperty()
    RegisteredServices__service_name = ndb.StringProperty()
    host_name = ndb.StringProperty()
    service_ip = ndb.StringProperty()
    record_created = ndb.DateTimeProperty(default=dt.now())
    is_online = ndb.BooleanProperty()
    offline_date = ndb.DateTimeProperty()
