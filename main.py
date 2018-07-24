"""`main` is the top level module for your Pyramid application."""

# Import the Pyramid Framework
from pyramid.config import Configurator
from pyramid.response import Response
from dbquery import models
from dbquery.routes import routes as db_routes

def root_page(request):
    """Return a friendly greeting."""
    md = models.Model()
    User = md.get_model_by_name('User')
    if User:
        k = User(first_name='Raul', last_name='Gonzalez').put()
    else:
        k = 'Fail'
    return Response('Hello World! '+str(k))


config = Configurator()

routes = [
    ('root', '/', root_page)
]

routes = db_routes + routes
for route in routes:
    name, uri, handler = route
    config.add_route(name, uri)
    config.add_view(handler, route_name=name)


# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
app = config.make_wsgi_app()
