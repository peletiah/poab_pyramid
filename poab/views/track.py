from pyramid.response import Response
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    )
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from poab.models import (
    DBSession,
    Track,
    Trackpoint
    )
from sqlalchemy import and_

from datetime import timedelta
import time,datetime, json

from decimal import Decimal, ROUND_HALF_UP


def generate_json_from_tracks(tracks):
    features=list()
    for row in tracks:
        if row.reduced_trackpoints:
            rounded_distance='<b>distance:</b> %skm<br />' % (str(Decimal(row.distance).quantize(Decimal("0.01"), ROUND_HALF_UP)))
            total_mins = row.timespan.seconds / 60
            mins = total_mins % 60
            hours = total_mins / 60
            timespan = '<b>duration:</b> %sh%smin<br />' % (str(hours),str(mins))
            date=row.start_time.strftime('%B %d, %Y')
            color='#'+row.color
            reduced_track = list() 
            features.append(
                (dict(
                type='Feature', 
                geometry=dict(
                    type="LineString", 
                    coordinates=row.reduced_trackpoints
                    ),
                properties=dict(
                    type = 'line',
                    date = date,
                    distance = rounded_distance,
                    timespan = timespan,
                    color = color
                    ),
                )))
    tracks_json = 'OpenLayers.Protocol.Script.registry.c1('+json.dumps(dict(type='FeatureCollection', features=features))+')'
    return tracks_json

def generate_json_from_trackpoint(trackpoint):
    trackpoint_json = '''OpenLayers.Protocol.Script.registry.c1({"type":"Feature","geometry":{"type":"Point","coordinates": [%s,%s] }, "properties": {"type":"point"}})''' % (str(trackpoint.longitude), str(trackpoint.latitude))
    return trackpoint_json



@view_config(route_name='json_track')
@view_config(route_name='json_track:action')
def json_track_view(request):
    try:
        action=request.matchdict['action']
    except:
        action='c'
    try:
        id=int(request.matchdict['id'])
    except:
        id=0
    if action=='c' and id==0:
        after_date = datetime.datetime.strptime('2010-09-02',"%Y-%m-%d")
        before_date = datetime.datetime.strptime('2013-12-07', "%Y-%m-%d")
        curr_date = after_date
        tracks = DBSession.query(Track).filter(and_(Track.start_time > after_date, Track.id != 141)).all()
        response = Response(generate_json_from_tracks(tracks))
    elif action=='c':
        trackpoints = DBSession.query(Trackpoint).filter(and_(Trackpoint.country_id==id,Trackpoint.infomarker==True)).all()
        trkpt_list=list()
        for trackpoint in trackpoints:
            trkpt_list.append(trackpoint.track_id)
        tracks = DBSession.query(Track).filter(Track.id.in_(trkpt_list)).all()
        response = Response(generate_json_from_tracks(tracks))
    elif action=='infomarker':
        infomarker = DBSession.query(Trackpoint).filter(Trackpoint.id==id).one()
        tracks = DBSession.query(Track).filter(Track.id==infomarker.track_id).all()
        response = Response(generate_json_from_tracks(tracks))
    elif action=='fromgpx':
        tracks = DBSession.query(Track).filter(Track.id==id).all()
        response = Response(generate_json_from_tracks(tracks))
    elif action=='simple':
        trackpoint = DBSession.query(Trackpoint).filter(Trackpoint.id==id).one()
        response = Response(generate_json_from_trackpoint(trackpoint))
    else:
        after_date = datetime.datetime.strptime('2010-09-02',"%Y-%m-%d")
        before_date = datetime.datetime.strptime('2010-12-07', "%Y-%m-%d")
        curr_date = after_date
        tracks = DBSession.query(Track).filter(and_(Track.date > after_date, Track.date < before_date)).all()
        response = Response(generate_json_from_tracks(tracks))
    response.content_type = 'application/json'
    return(response)

@view_config(route_name='track',
            renderer='track/track.mako',
)
@view_config(route_name='track:action',
            renderer='track/track.mako',
)
def track_view(request):
    try:
        action=request.matchdict['action']
    except:
        action='c'
    try:
        id=int(request.matchdict['id'])
    except:
        id=0
    jsonlink='/json_track/%s/%s' % (action, id)
    return {
        'action': action,
        'id': id,
        'request': request,
        'jsonlink': jsonlink,
    }
    


