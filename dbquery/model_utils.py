import json

from _base.common import common_models


def props(cls):
    return [i for i in cls.__dict__.keys() if i[:1] != '_']


def model_to_dict(model):
    model_dict = dict()
    model_dict['name'] = model.__class__.__name__

    properties = props(model)
    properties_meta = dict()

    for prop in properties:
        properties_meta[prop] = {
            'type': prop.__class__.__name__
        }

    model_dict['properties'] = properties_meta

    return model_dict


def model_to_json(model):
    model_dict = model_to_dict(model)
    model_json = json.dumps(model_dict)
    return model_json


def dict_to_model(model_dict):
    a_model = common_models.BaseModel()

    properties = model_dict.get('properties')
    for prop in properties.keys():
        prop_type = properties[prop]['type']
        setattr(a_model, prop, __import__(prop_type))

    return a_model


def json_to_model(model_json):
    model_dict = json.loads(model_json)

    return dict_to_model(model_dict)
