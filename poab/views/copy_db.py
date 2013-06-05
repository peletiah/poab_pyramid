
from pyramid.response import Response
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    HTTPFound,
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

from poab.helpers import flickrtools, filetools, imagetools, timetools

import markdown
import os

import poab.helpers.douglaspeucker as dp


from decimal import Decimal, ROUND_HALF_UP

from poab.models import (
    DBSession,
    Log,
    LogOld,
    Track,
    TrackOld,
    Trackpoint,
    TrackpointOld,
    Location,
    Image,
    Imageinfo,
    Timezone,
    Country,
    Continent,
    FlickrImage
    )

import re


def reduce_trackpoints(trackpoints, factor):
    points = list()
    reduced_trackpoints = list()
    for pt in trackpoints:
        points.append(dp.Vec2D( float(pt.longitude) , float(pt.latitude) ))
    line = dp.Line(points)
    dp_trkpts_reduced = line.simplify(factor) #simplified douglas peucker line
    for trackpoint in dp_trkpts_reduced.points:
        reduced_trackpoints.append([trackpoint.coords[0],trackpoint.coords[1]]) #list of simplified trackpoints
    return reduced_trackpoints

@view_config(
    route_name='copy_db'
)
def copy_db(request):
    #tracks_old = DBSession.query(TrackOld).filter(TrackOld.id == 141).all()

#TRACK/TRACKPOINT

#    #tracks_old = DBSession.query(TrackOld).filter(TrackOld.id == 141).all()
#    tracks_old = DBSession.query(TrackOld).all()
#    print tracks_old
#    for track_old in tracks_old:
#        track_query = DBSession.query(Track).filter(Track.id == track_old.id)
#        if track_query.count() < 1:
#            start_time = track_old.date
#            end_time = track_old.date
#            trackpoint_count = track_old.trkptnum
#            distance = str(track_old.distance)
#            timespan = track_old.timespan
#            color = track_old.color 
#            track = Track(
#                id = track_old.id,
#                start_time = start_time,
#                end_time = end_time,
#                trackpoint_count = trackpoint_count,
#                distance = distance,
#                timespan = timespan,
#                color = color,
#                reduced_trackpoints = None,
#                author = 1,
#                etappe = 1,
#                uuid = None
#                )
#            DBSession.add(track)
#            print track_old.distance
#            print track.distance
#            trackpoints_old = DBSession.query(TrackpointOld).filter(TrackpointOld.track_id == track.id).all()
#            trackpoint_list=list()
#            for trackpoint_old in trackpoints_old:
#                #print trackpoint_old.altitude,trackpoint_old.velocity,trackpoint_old.temperature,trackpoint_old.direction,trackpoint_old.pressure
#                trackpoint = Trackpoint(
#                                id = trackpoint_old.id,
#                                track_id = track.id,
#                                latitude = trackpoint_old.latitude,
#                                longitude = trackpoint_old.longitude,
#                                altitude = trackpoint_old.altitude,
#                                velocity = trackpoint_old.velocity,
#                                temperature = trackpoint_old.temperature,
#                                direction = trackpoint_old.direction,
#                                pressure = trackpoint_old.pressure,
#                                timestamp = trackpoint_old.timestamp,
#                                uuid = None
#                                )
#                DBSession.add(trackpoint)
#                if trackpoint_old.location or trackpoint_old.country_id:
#                    location = Location(
#                            trackpoint_id = trackpoint.id,
#                            country_id = trackpoint_old.country_id,
#                            name = trackpoint_old.location
#                            )
#                    DBSession.add(location)
#                trackpoint_list.append(trackpoint)
#            
#            trackpoint_list.sort(key = lambda trackpoint: trackpoint.timestamp)
#            if track_old.id != 140 and track_old.id != 145:
#                reduced_trkpts=reduce_trackpoints(trackpoint_list, 0.0002)
#                track.reduced_trackpoints = reduced_trkpts
#                print reduced_trkpts
#            DBSession.add(track)
#        else:
#            track = track_query.one()
#
#    #TRACKPOINTS with Track
#    trackpoints_unlinked = DBSession.query(TrackpointOld).filter(TrackpointOld.track_id == None).all()
#    trackpoint_list=list()
#    for trackpoint_unlinked in trackpoints_unlinked:
#        #print trackpoint_old.altitude,trackpoint_old.velocity,trackpoint_old.temperature,trackpoint_old.direction,trackpoint_old.pressure
#        trackpoint = Trackpoint(
#                        id = trackpoint_unlinked.id,
#                        track_id = track.id,
#                        latitude = trackpoint_unlinked.latitude,
#                        longitude = trackpoint_unlinked.longitude,
#                        altitude = trackpoint_unlinked.altitude,
#                        velocity = trackpoint_unlinked.velocity,
#                        temperature = trackpoint_unlinked.temperature,
#                        direction = trackpoint_unlinked.direction,
#                        pressure = trackpoint_unlinked.pressure,
#                        timestamp = trackpoint_unlinked.timestamp,
#                        uuid = None
#                        )
#        DBSession.add(trackpoint)
#        if trackpoint_unlinked.location or trackpoint_unlinked.country_id:
#            location = Location(
#                    trackpoint_id = trackpoint.id,
#                    country_id = trackpoint_unlinked.country_id,
#                    name = trackpoint_unlinked.location
#                    )
#            DBSession.add(location)
#
#
##LOG
#
#    #logs_old = DBSession.query(LogOld).filter(LogOld.id==446).all()
#    logs_old = DBSession.query(LogOld).all()
#    
#    for log_old in logs_old:
#        log_query = DBSession.query(Log).filter(Log.id == log_old.id)
#        if log_query.count() < 1:
#            content = log_old.content
#            imgid_tag_list = re.findall("(\[imgid[0-9A-Za-z-]{1,}\])", content)
#            for tag in imgid_tag_list:
#                print tag
#                imgid=re.search("^\[imgid([0-9A-Za-z-]{1,})\]$",tag).group(1)
#                content=content.replace(tag,('[imgid=%s]') % imgid)
#            log = Log(
#                    id = log_old.id,
#                    infomarker = log_old.infomarker_id,
#                    topic = log_old.topic,
#                    content = content,
#                    created = log_old.createdate,
#                    etappe = 1,
#                    author = 1,
#                    uuid = None
#                )
#            DBSession.add(log)
#            DBSession.flush()
#        else:
#            log=log_query.one()
#        track = DBSession.query(Track).filter(Track.id == log.trackpoint_log_ref.track_id).one()
#        log.track.append(track)
#        
#
#IMAGE

    #images_old = DBSession.query(Imageinfo).filter(Imageinfo.log_id==446).all() 
    images_old = DBSession.query(Imageinfo).all() 
    for image_old in images_old:
        image_query = DBSession.query(Image).filter(Image.id == image_old.id)
        if image_query.count() < 1:

            name = image_old.imgname.split('/')[-1]
            location_old = image_old.imgname
            #location_old_prefix = '/srv'
            location_old_prefix = '/media/backup2/images/images_backup2/srv'
            basedir = '/srv/trackdata/bydate'
            img_large_w='990' #width of images in editor-preview
            img_medium_w='500' #width of images in editor-preview
            img_thumb_w='150' #width of images in editor-preview

            print location_old.split('/')[-5]
            if re.findall("best",location_old):
                location_old_fullsize = location_old_prefix+location_old.replace(location_old.split('/')[-2]+'/','best/')
                location_new = filetools.createdir('/srv/trackdata/bydate','christian',location_old.split('/')[-4])+'images/sorted/'
                os.popen('/bin/cp %s %s' %(location_old_fullsize, location_new))
                imagetools.resize(location_new, location_new+img_large_w+'/', name, img_large_w)
            else:
                location_old_fullsize = location_old_prefix+location_old.replace(location_old.split('/')[-2]+'/','')
                location_new = filetools.createdir('/srv/trackdata/bydate','christian',location_old.split('/')[-5])+'images/sorted/'
                os.popen('/bin/cp %s%s %s%s/' %(location_old_prefix, location_old, location_new, img_large_w))
                os.popen('/bin/cp %s %s' %(location_old_fullsize, location_new))
                
            print location_old_prefix+location_old
            print location_old_fullsize
            print location_new
            imagetools.resize(location_new, location_new+img_medium_w+'/', name, img_medium_w)
            imagetools.resize(location_new, location_new+img_thumb_w+'/', name, img_thumb_w)
            image = Image(
                    id = image_old.id,
                    name = name,
                    location = location_new,
                    title = image_old.flickrtitle,
                    comment = image_old.flickrdescription,
                    alt = None,
                    aperture = image_old.aperture,
                    shutter = image_old.shutter,
                    focal_length = image_old.focal_length,
                    iso = image_old.iso,
                    timestamp_original = image_old.flickrdatetaken,
                    hash = image_old.photohash,
                    hash_large = image_old.photohash_990, #TODO: we need the real file's hash if 990px was uploaded and not converted
                    author = 1,
                    trackpoint = image_old.trackpoint_id,
                    last_change = timetools.now(),
                    published = timetools.now(),
                    uuid = None
                    )
            DBSession.add(image)
            DBSession.flush()
            flickr = FlickrImage(
                image = image.id,
                farm = image_old.flickrfarm,
                server = image_old.flickrserver,
                photoid = image_old.flickrphotoid,
                secret = image_old.flickrsecret
            )
            DBSession.add(flickr)
            DBSession.flush()
        else:
            image = image_query.one()
        log=DBSession.query(Log).filter(Log.id == image_old.log_id).one()
        log.image.append(image)
        

    return Response('ok')
