from pyramid.response import Response
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    )
from pyramid.view import view_config

import poab.helpers.douglaspeucker as dp

from sqlalchemy.exc import DBAPIError

from poab.models import (
    DBSession,
    Track,
    Trackpoint,
    now
    )

from sqlalchemy import and_

from lxml import etree
from xml.etree import ElementTree

from datetime import timedelta
import time,datetime

from decimal import Decimal, ROUND_HALF_UP



def reduce_trackpoints(trackpoints):
    points = []
    for pt in trackpoints:
        points.append(dp.Vec2D( float(pt.longitude) , float(pt.latitude) ))
    line = dp.Line(points)
    return line.simplify(0.0002)


def create_json_for_db(reduced_tkpts):
            json_string =  '{"type":"Feature","geometry":{"type":"LineString","coordinates":['
            for trackpoint in reduced_tkpts.points:
                json_string = json_string + '[%s,%s],' % (trackpoint.coords[0],trackpoint.coords[1])
            json_string=json_string[:-1]+']}}\n'
            return json_string


@view_config(route_name='gpximport',
            renderer='gpximport/gpximport.mako')
def gpximport(request):
    return {}


@view_config(route_name='gpxprocess')
def gpxprocess(request):
    class trkpt:
        def __init__(self, latitude, longitude):
            self.latitude = latitude
            self.longitude = longitude
    
    trkptlist=list()
    
    gpx_ns = "http://www.topografix.com/GPX/1/1"
    filename = request.POST['gpx'].filename
    input_file = request.POST['gpx'].file

    root = etree.parse(input_file).getroot()
    trackSegments = root.getiterator("{%s}trkseg"%gpx_ns)
    for trackSegment in trackSegments:
        for trackPoint in trackSegment:
            lat=trackPoint.attrib['lat']
            lon=trackPoint.attrib['lon']
            new_trkpt=trkpt(lat,lon)
            trkptlist.append(new_trkpt)
    
    reduced_trkpts=reduce_trackpoints(trkptlist)
    json_string=create_json_for_db(reduced_trkpts)
    track=Track(now(),len(trkptlist),0,'00:00:00',None,None,None,None,None,None,None,json_string)
    DBSession.add(track)
    DBSession.flush()
    #raise HTTPFound(request.route_url('track','fromgpx',track.id))
    route=request.route_url('track','fromgpx',track.id)
    response = Response('<a href="%s">%s</a>' % (route,route))
    response.content_type = 'text/html'
    return(response)


