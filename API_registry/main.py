import socket
from dbquery import models

def Build():

    host_name = socket.gethostname()
    md = models.Model()
    API = md.get_model_by_name('API_Registry')
    #if API:
    #    return API(service_name='CoreModules', host_name=host_name).put()

    #return 'API Failed'

