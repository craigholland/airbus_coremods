"""`main` is the top level module for your Pyramid application."""

# Import the Pyramid Framework
from pyramid.config import Configurator
from pyramid.response import Response


def hello_world(request):
    """Return a friendly greeting."""
    return Response('Hello World!')

config = Configurator()
config.add_route('root', '/')
config.add_view(hello_world, route_name='root')

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
app = config.make_wsgi_app()
