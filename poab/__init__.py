from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import DBSession

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('log', '/log')
    config.add_route('log:action', '/log/{action}/{id}{page:.*}')
    config.add_route('view', '/view')
    config.add_route('view:action', '/view/{action}/{id}{page:.*}')
    config.add_route('svg', '/misc/country_svg/{country_id}')
    config.add_route('track', '/track')
    config.add_route('track:action', '/track/{action}/{id}{imageid:.*}')
    config.add_route('json_track', '/json_track')
    config.add_route('json_track:action', '/json_track/{action}/{id}{imageid:.*}')
    config.add_route('about', '/about')
    config.add_route('test', '/test')
    config.add_route('test:action', '/test/{bla}/{blu}/{page}')
    config.scan()
    return config.make_wsgi_app()

