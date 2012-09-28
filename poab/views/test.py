from pyramid.response import Response
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    )

from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from sqlalchemy import (
    asc,
    and_
)

from poab.helpers.fractions import (
    Fraction
)

import markdown

from decimal import Decimal, ROUND_HALF_UP

from poab.models import (
    DBSession,
    Log,
    Track,
    Trackpoint,
    Imageinfo,
    Timezone,
    Country,
    Continent
    )

import re



@view_config(
    route_name='test',
    renderer='test.mako',
)
@view_config(
    route_name='test:action',
    renderer='test.mako',
)
def test_view(request):
    try:
        bla=request.matchdict['bla']
    except:
        bla='c'
    try:
        blu=request.matchdict['blu']
    except:
        blu=0
    try:
        page=int(request.matchdict['page'])
    except:
        page=0

    return {
        'bla': bla,
        'blu': blu,
        'page': page,
        'request': request,
    }


