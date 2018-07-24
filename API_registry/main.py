import socket
from dbquery import models as db_model
from API_registry import models
from pyramid.response import Response
from pyramid.view import view_config

md = db_model.Model()

def _APIRegistry_isOnline():
    return md.get_model_by_name('API_Registry') is not None


def Build():
    host_name = socket.gethostname()

    API = md.get_model_by_name('API_Registry')
    if API:
       API(service_name='CoreModules', host_name=host_name).put()

def Listall(request):
    md = db_model.Model()
    response = 'failed'
    if _APIRegistry_isOnline:
        API = md.get_model_by_name('API_Registry')
        services = API.query(
            API.is_online == True).fetch(
            projection=[API.host_name, API.service_name])
        response = str(services)
    return Response(response)

@view_config(route_name='apireg_list')
def List(request):
    service = request.matchdict["mod"]
    response='None'
    if service and _APIRegistry_isOnline():
        API = md.get_model_by_name('API_Registry')
        hosts = API.query(
            API.is_online == True,
            API.service_name == service).fetch(
            projection=[API.host_name])
        response = str(hosts)
    return Response(response)


@view_config(route_name='apireg_offline')
def HostOffline(request):
    hostname = request.matchdict["mod"]
    response = 'None'
    if hostname and _APIRegistry_isOnline():
        API = md.get_model_by_name('API_Registry')
        hosts = API.query(
            keys_only=True).filter(
            API.is_online == True,
            API.host_name == hostname).fetch()
        for key in hosts:
            key.is_online=False
            key.put()


