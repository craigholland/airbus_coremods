from datetime import datetime as dt
from google.appengine.api import memcache
from google.appengine.ext import ndb

from _base.common import common_models

class User(common_models.BaseModel):
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()

class Product(common_models.BaseModel):
    name = ndb.StringProperty()
    price = ndb.FloatProperty()
    manufacturer = ndb.StringProperty()

class ProductOptions(common_models.BaseModel):
    Product__key_name = ndb.StringProperty()
    ProductOptions__key_name = ndb.StringProperty()
    option_name = ndb.StringProperty()

class Inventory(common_models.BaseModel):
    Product__key_name = ndb.StringProperty()
    ProductOptions__key_name = ndb.StringProperty()
    quantity = ndb.IntegerProperty()

class CartProfile(common_models.BaseModel):
    User__key_name = ndb.StringProperty()
    session_id = ndb.StringProperty()
    cart_name = ndb.StringProperty()
    cart_created = ndb.DateTimeProperty(default=dt.now())
    cart_updated = ndb.DateTimeProperty(default=dt.now())

class CartItems(common_models.BaseModel):
    CartProfile__key_name = ndb.StringProperty()
    Product__key_name = ndb.StringProperty()
    ProductOptions__key_name = ndb.StringProperty()
    quantity = ndb.IntegerProperty(default=0)
    purchase_date = ndb.DateTimeProperty()
