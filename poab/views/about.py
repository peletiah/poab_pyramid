from pyramid.response import Response
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    HTTPFound,
    )


from pyramid.view import view_config


@view_config(
    route_name='about',
    renderer='about/about.mako',
)
def about_view(request):
    return {
        'request':request
    }
