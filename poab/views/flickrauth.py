import flickrapi
from pyramid.response import Response
from pyramid.view import view_config


@view_config(route_name='flickrauth')
def flickr_auth_handler(request):
    api_key = '80ea42af0f13e85c5a40a3eb8e610612'
    api_secret = 'f9edc879845ade72'
    flickr = flickrapi.FlickrAPI(api_key, api_secret, username='daniela')
    print(request.params)
    frob = request.params['frob']
    print(frob)
    flickr.get_token(frob)
    return Response(frob)



