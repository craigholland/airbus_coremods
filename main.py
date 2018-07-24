"""`main` is the top level module for your Pyramid application."""
import socket
# Import the Pyramid Framework
from pyramid.config import Configurator
from pyramid.response import Response
from dbquery import models
from dbquery import main as db_main
from dbquery.routes import routes as db_routes
from API_registry import main as API
from API_registry import models as API_models

config = Configurator()

def root_page(request):
    """Return a friendly greeting."""
    md = models.Model()
    User = md.get_model_by_name('User')
    if User:
        k = User(first_name='Raul', last_name='Gonzalez').put()
    else:
        k = 'Fail'
    return Response('Front Page '+str(k))

_routes = [
    ('root', '/', root_page)
]

_HOST_NAME = socket.gethostname()
db_main.build(API_models.API_Registry)
start_key = API.Build(_HOST_NAME)

routes = db_routes + _routes
for route in routes:
    name, uri, handler = route
    config.add_route(name, uri)
    config.add_view(handler, route_name=name)

app = config.make_wsgi_app()
