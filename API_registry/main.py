import socket
from dbquery import models as db_model
from API_registry import models
from pyramid.response import Response
from pyramid.view import view_config

md = db_model.Model()

def _APIRegistry_isOnline():
    return md.get_model_by_name('API_Registry') is not None

def _addService(service_name):
    """Checks to see if service exists. Adds if unique."""
    md = models.RegisteredServices
    key = md.query(md.service_name == service_name).fetch(1)
    if key:
        return key[0].key
    else:
        return md(service_name=service_name).put()

@view_config(route_name='apireg_regsrv')
def RegisterService(request):
    service = request.matchdict["mod"]
    return Response(str(_addService(service)))

def getRegServicesList(request):
    md = models.RegisteredServices
    rs_list = [rs.key.service_name for rs in md.query().fetch(keys_only=True)]

    return Response(str(rs_list))

def Build(service_name):
    """Establish Service in Registry"""

    srvc_entity = _addService(service_name).get()
    host_name = socket.gethostname()
    if host_name.find('//'):
        host_name = host_name[host_name.find('//')+2:]

    API = md.get_model_by_name('API_Registry')
    if API:
       API(RegisteredServices__key_name=srvc_entity.key_name,
           RegisteredServices__service_name=srvc_entity.service_name,
           host_name=host_name, is_online=True).put()

def Listall(request):
    md = db_model.Model()
    response = 'failed'
    if _APIRegistry_isOnline():
        API = md.get_model_by_name('API_Registry')
        services = API.query(
            API.is_online == True).fetch(
            projection=[API.host_name, API.RegisteredServices__service_name])
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
            API.RegisteredServices__service_name == service).fetch(
            projection=[API.host_name])
        response = str(hosts)
    return Response(response)


@view_config(route_name='apireg_offline')
def HostOffline(request):
    hostname = request.matchdict["mod"]
    response = 'None'
    host_results = []
    if hostname and _APIRegistry_isOnline():
        API = md.get_model_by_name('API_Registry')
        hosts = API.query(
            ).filter(
            API.is_online == True,
            API.host_name == hostname
            ).fetch(keys_only=True)
        for key in hosts:
            ent = key.get()
            ent.is_online=False
            host_results.append(ent.put())
    return Response(str(host_results))


