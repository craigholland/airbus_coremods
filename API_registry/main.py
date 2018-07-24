from API_registry import models
import socket

def Build(host_name):
    IPaddr = socket.gethostbyname(host_name)
    return models.API_Registry(
        service_name='CoreModules',
        host_name=host_name,
        service_ip=IPaddr
    ).put()







