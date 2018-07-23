from datetime import datetime as dt
from google.appengine.ext import ndb
from _base.common import common_models
from dbquery import models
from pyramid.response import Response


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
def Build(model):
    if isinstance(model, list) or isinstance(model, tuple):
        for m in model:
            Build(m)
    elif isinstance(model, common_models.BaseModel):
        models.Model.add(model)


    return Response('added models')

def List(request):
    models = []
    for x in [y for y in dir(models.AllModels) if not y.startswith('_')]:
        if isinstance(x, common_models.BaseModel):
            models.append[x]
    return Response(str(models))
