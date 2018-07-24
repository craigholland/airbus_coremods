import socket
from dbquery import models as db_model
from API_registry import models
from pyramid.response import Response

md = db_model.Model()

def _APIRegistry_isOnline():
    return md.get_model_by_name('API_Registry') is not None


def Build():
    host_name = socket.gethostname()

    API = md.get_model_by_name('API_Registry')
    if API:
       API(service_name='CoreModules', host_name=host_name).put()

def Listall():
    response = 'failed'
    if _APIRegistry_isOnline:
        API = md.get_model_by_name('API_Registry')
        services = API.query(
            API.is_online == True).fetch(
            projection=[API.host_name, API.service_name])
        response = str(services)
    Response(response)

def List(request):
    pass

def Update(request):
    pass



