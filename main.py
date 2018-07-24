"""`main` is the top level module for your Pyramid application."""
import socket
# Import the Pyramid Framework
from pyramid.config import Configurator
from pyramid.response import Response
from dbquery import models
from dbquery import main as db_main
from dbquery.routes import routes as db_routes
from API_registry.routes import routes as api_routes
from API_registry.main import Build
from API_registry import models as API_models

config = Configurator()


def root_page(request):
    """Start it up."""
    # Create API Registry model and announce being online.
    md = models.Model()
    if not md.get_model_by_name('API_Registry'):
        db_main.build(API_models.API_Registry)
        Build()


    if md.get_model_by_name('API_Registry'):
        result = 'API Registry ready...'
    else:
        result = 'API Registry failed to build'

    return Response('Core Modules Running: ' + result)


# Get Routes from Modules
_routes = [
    ('root', '/', root_page)
]

routes = db_routes + api_routes + _routes
for route in routes:
    name, uri, handler = route
    config.add_route(name, uri)
    config.add_view(handler, route_name=name)

# Start it up
app = config.make_wsgi_app()