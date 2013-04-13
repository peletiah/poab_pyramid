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
    Author,
    FlickrCredentials
    )

import hashlib, json


from time import strftime
import uuid, flickrapi

@view_config(route_name='flickrauth')
def flickr_auth_handler(request):
    api_key = '80ea42af0f13e85c5a40a3eb8e610612'
    api_secret = 'f9edc879845ade72'
    flickr = flickrapi.FlickrAPI(api_key, api_secret, username='daniela')
    perms='delete'
    print request.params
    frob = request.params['frob']
    print frob
    flickr.get_token(frob)
    return Response(frob)
    
    

