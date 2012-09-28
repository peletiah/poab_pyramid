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
    Trackpoint,
    )
from sqlalchemy import and_

from datetime import timedelta
import time,datetime

from decimal import Decimal, ROUND_HALF_UP


def generate_json_from_tracks(tracks):
    tracks_json = 'OpenLayers.Protocol.Script.registry.c1({"type":"FeatureCollection","features":['
    for row in tracks:
        if row.json_0002:
            rounded_distance='<b>distance:</b> %skm<br />' % (str(row.distance.quantize(Decimal("0.01"), ROUND_HALF_UP)))
            total_mins = row.timespan.seconds / 60
            mins = total_mins % 60
            hours = total_mins / 60
            timespan = '<b>duration:</b> %sh%smin<br />' % (str(hours),str(mins))
            date=row.date.strftime('%B %d, %Y')
            color='#'+row.color
            linestring = str(row.json_0002).replace('}}',('},"properties": {"type":"line","date":"%s","distance":"%s","timespan":"%s","color":"%s"}}') % (date,rounded_distance,timespan,color))
            tracks_json = tracks_json + linestring + ','
    tracks_json = tracks_json[:-1] + ']})'
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
        before_date = datetime.datetime.strptime('2010-12-07', "%Y-%m-%d")
        curr_date = after_date
        tracks = DBSession.query(Track).filter(and_(Track.date > after_date, Track.date < before_date)).all()
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
    elif action=='simple':
        trackpoint = DBSession.query(Trackpoint).filter(Trackpoint.id==id).one()
        response = Response(generate_json_from_trackpoint(trackpoint))
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
    


