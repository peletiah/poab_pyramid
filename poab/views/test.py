from pyramid.view import view_config


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


