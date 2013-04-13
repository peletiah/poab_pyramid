from lxml import etree
from xml.etree import ElementTree

from datetime import timedelta
import time,datetime

import json, re

from decimal import Decimal, ROUND_HALF_UP

import poab.helpers.douglaspeucker as dp

from poab.models import (
    DBSession,
    Author,
    Log,
    Track,
    Trackpoint,
    Image,
    Imageinfo,
    Timezone,
    Country,
    Continent
    )



def reduce_trackpoints(trackpoints):
    points = []
    for pt in trackpoints:
        points.append(dp.Vec2D( float(pt.longitude) , float(pt.latitude) ))
    line = dp.Line(points)
    return line.simplify(0.0002)


def create_json_for_db(reduced_tkpts):
            trackpoint_list = list()
            for trackpoint in reduced_tkpts.points:
                trackpoint_list.append([trackpoint.coords[0],trackpoint.coords[1]])
            json_string=json.dumps(dict(type='Feature',geometry=dict(type='LineString',coordinates=trackpoint_list)))
            return json_string


def gpxprocess(gpxfile):
    file = open(gpxfile,'r')
    class trkpt:
        def __init__(self, latitude, longitude):
            self.latitude = latitude
            self.longitude = longitude

    trkptlist=list()

    gpx_ns = "http://www.topografix.com/GPX/1/1"

    root = etree.parse(gpxfile).getroot()
    trackSegments = root.getiterator("{%s}trkseg"%gpx_ns)
    for trackSegment in trackSegments:
        for trackPoint in trackSegment:
            lat=trackPoint.attrib['lat']
            lon=trackPoint.attrib['lon']
            new_trkpt=trkpt(lat,lon)
            trkptlist.append(new_trkpt)

    reduced_trkpts=reduce_trackpoints(trkptlist)
    json_string=create_json_for_db(reduced_trkpts)
    file.close()
    return json_string



def parse_trackpoints(trackpoints, gpx_ns):
    for trackpoint in trackpoints:
        lat = trackpoint.attrib['lat']
        lon = trackpoint.attrib['lon']
        elevation = trackpoint.find('{%s}ele'% gpx_ns).text
        time_str = trackpoint.find('{%s}time'% gpx_ns).text.replace('T',' ')[:-1]
        time = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        trackpoint = Trackpoint(track_id=None, latitude=lat, longitude=lon, altitude=None, velocity=None, temperature=None, direction=None, pressure=None, timestamp=time)
        DBSession.add(trackpoint)
        DBSession.flush()
        

def track_description(track_desc):
    #regex match of track description, save values in re-groups
    metrics=re.compile(r'Total Track Points: (?P<pts>\d+). Total time: (?P<h>\d+)h(?P<m>\d+)m(?P<s>\d+)s. Journey: (?P<distance>\d+.\d+)Km').match(track_desc)
    pts_num = int(metrics.group("pts")) #number of trackpoints in this track
    hours = int(metrics.group("h"))
    minutes = int(metrics.group("m"))
    seconds = int(metrics.group("s"))
    timespan = timedelta(hours=hours, minutes=minutes, seconds=seconds)
    distance = float(metrics.group("distance"))
    return pts_num, timespan, distance


def parse_gpx(gpxfile):
    file = open(gpxfile,'r')
    gpx_ns = "http://www.topografix.com/GPX/1/1"
    root = etree.parse(gpxfile).getroot()
    tracks = root.getiterator("{%s}trk"%gpx_ns)

    for track in tracks:
        #TODO: First check if track with these trackpoints already exists
        #TODO: We need a track_id for all trackpoints
        trackpoints = track.getiterator("{%s}trkpt"%gpx_ns)
        parse_trackpoints(trackpoints, gpx_ns)

        track_desc = track.find('{%s}desc'% gpx_ns).text
        pts_num, timespan, distance = track_description(track_desc)
        print timespan, distance
    


        





