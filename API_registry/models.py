import protorpc
from datetime import datetime as dt

from google.appengine.ext import ndb
from _base.common import common_models

class API_Registry(common_models.BaseModel):
    service_name = ndb.StringProperty(1, required=True)
    host_name = ndb.StringProperty(2)
    service_ip = ndb.StringProperty(3, required=True)
    record_created = ndb.DateTimeProperty(4, default=dt.now())
    is_online = ndb.BooleanProperty(5, default=True)
    offline_date = ndb.DateTimeProperty(6)
