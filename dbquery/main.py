from datetime import datetime as dt
from google.appengine.ext import ndb
from _base.common import common_models
from dbquery import models
from pyramid.response import Response
import inspect

class Product(common_models.BaseModel):
    name = ndb.StringProperty()
    price = ndb.FloatProperty()
    manufacturer = ndb.StringProperty()

class User(common_models.BaseModel):
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()

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

model=[Product, User, ProductOptions, Inventory, CartProfile, CartItems]
def Build(request, mdl=model):
    md = models.Model()
    results = []
    if isinstance(mdl, list) or isinstance(mdl, tuple):
        for m in mdl:
            results.append(models.addToModel(m))
    else:
        results.append(models.addToModel(mdl))

    res = ''
    for r in results:
        res += '{0}<br>'.format(str(r))
    return Response(res)

def List(request):
    md = models.Model()
    return Response(str([y for y in dir(md) if not y.startswith('_')]))

