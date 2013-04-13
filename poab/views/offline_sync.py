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
    Log,
    Track,
    Trackpoint,
    Image,
    Imageinfo,
    Timezone,
    Country,
    Continent
    )

import hashlib, json

from poab.helpers import (
    timetools,
    imagetools,
    filetools,
    flickrtools,
    gpxtools
    )

from datetime import datetime
import uuid

@view_config(route_name='sync', request_param='type=status')
def itemstatus(request):
    filetype = request.POST.get('filetype')
    metadata = json.loads(request.POST.get('metadata'))
    if filetype == 'image':
        image = Image.get_image_by_uuid(metadata['uuid'])
        if not image:
            image = Image.get_image_by_hash(metadata['hash'])
            #TODO: image.hash is different than in our db, why?
        if image:
            print 'Image found! '+image.location
            image_bin = open(image.location+image.name, 'rb')
            hash=hashlib.sha256(image_bin.read()).hexdigest()
            if hash == image.hash == metadata['hash']:
                print 'Image already exists on server!'
                return Response(json.dumps({'sync_status':'was_synced'}))
            else:
                print 'Imagehash mismatch!'
                return Response(json.dumps({'sync_status':'sync_error'}))

    if filetype == 'track':
        track = Track.get_track_by_uuid(metadata['uuid'])
        #if not track:
        #    track = Track.get_track_by_hash(metadata['hash'])
        #    #TODO: track.hash is different than in our db, why?
        #print track
        #if track:
        #    print 'Trac found! '+track.location
        #    track_bin = open(track.location+track.name, 'rb')
        #    hash=hashlib.sha256(track_bin.read()).hexdigest()
        #    if hash == track.hash == metadata['hash']:
        #        print 'Track already exists on server!'
        #        return Response(json.dumps({'sync_status':'was_synced'}))
        #    else:
        #        print 'Trackhash mismatch!'
        #        return Response(json.dumps({'sync_status':'sync_error'}))
 
    return Response(json.dumps({'sync_status':'not_synced'}))



@view_config(route_name='sync', request_param='type=log')
def logsync(request):
    log_json = json.loads(request.POST.get('log').value)
    print log_json
    log = Log.get_log_by_uuid(log_json['uuid']) #converts str-uuid to python-UUID, then looks up DB
    if not log:
        print 'No log found, adding new log.'
        print 'Author: '+log_json['author']
        author = Author.get_author(log_json['author'])
        log = Log(
                infomarker_id = None,
                topic=log_json['topic'],
                content=log_json['content'],
                author=author.id,
                created=log_json['created'],
                uuid=log_json['uuid']
                )
        DBSession.add(log)
        DBSession.flush()
        sync_status = 'is_synced'; #Item was not synced before we started
    elif log: #TODO: Updating log, needs last_change comparison and stuff
        print 'Log already exists on server'
        sync_status = 'was_synced' #Item was already on the server earlier        
    else:
        sync_status = 'sync_error' #something is wrong here!
    return Response(json.dumps({'item_uuid':str(log.uuid), 'item_id':log.id, 'log_id':log_json['id'], 'sync_status':sync_status}))
    
 


@view_config(route_name='sync', request_param='type=image')
def imagesync(request):
    print request.POST.keys()
    metadata = request.POST.get('metadata')
    log = json.loads(request.POST.get('log').value)
    image_bin = request.POST.get('image_bin')

    img_info = json.loads(metadata.value)
    author = Author.get_author(img_info['author'])


    image = Image.get_image_by_uuid(img_info['uuid']) #does image with this uuid(from json-info) already exist in our db
    if not image:

        basedir = '/srv/trackdata/bydate'
        img_prvw_w='500'
        img_990_w='990'
        created=datetime.strptime(log['created'], "%Y-%m-%d %H:%M:%S") #we use the timestamp from log.created for the image-location
        datepath=created.strftime("%Y-%m-%d")
        filedir = filetools.createdir(basedir, author.name, datepath)
        imgdir = filedir+'images/sorted/'

        filehash = filetools.safe_file(imgdir, img_info['name'], image_bin.value)

        imagetools.resize(imgdir, imgdir+img_prvw_w+'/', img_info['name'], img_prvw_w)
        imagetools.resize(imgdir, imgdir+img_990_w+'/',img_info['name'] , img_990_w) #TODO: what happens when a 990px-wide img was uploaded?

        hash_990=hashlib.sha256(open(imgdir+'990/'+img_info['name'], 'rb').read()).hexdigest() #TODO

        image = Image(
                    name = img_info['name'], 
                    location = imgdir, 
                    title = img_info['title'],
                    comment = img_info['comment'],
                    alt = img_info['alt'],
                    hash = filehash,
                    hash_990 = hash_990, #TODO: we need the real file's hash if 990px was uploaded and not converted
                    author = author.id,
                    last_change = timetools.now(),
                    published = timetools.now(),
                    uuid = img_info['uuid']
                    )
        DBSession.add(image)
        DBSession.flush()
        return Response(json.dumps({'item_uuid':image.uuid, 'item_id':image.id, 'log_id':log['id'], 'sync_status':'is_synced'}))

    else:
        #TODO: So our image is actually in the db - why has this not occured in sync?type=status??? 
        print 'ERROR: Image found in DB, but this should have happened in /sync?type=status'
        return Response(json.dumps({'item_uuid':image.uuid, 'item_id':image.id, 'log_id':log['id'], 'sync_status':'sync_error'}))
    
    return Response(json.dumps({'item_uuid':None, 'item_id':None, 'log_id':log['id'], 'sync_status':'sync_error'})) #Something went very wrong



@view_config(route_name='sync', request_param='type=track')
def tracksync(request):
    print request.POST.keys()
    metadata = request.POST.get('metadata')
    log = json.loads(request.POST.get('log').value)
    track_bin = request.POST.get('track_bin')
    track_info = json.loads(metadata.value)
    print track_info['author']

    author = Author.get_author(track_info['author'])


    track = Track.get_track_by_uuid(track_info['uuid']) #does track with this uuid(from json-info) already exist in our db
    if not track:

        basedir = '/srv/trackdata/bydate'
        created=datetime.strptime(log['created'], "%Y-%m-%d %H:%M:%S") #we use the log-created-timestamp for the track-location
        datepath=created.strftime("%Y-%m-%d")
        filedir = filetools.createdir(basedir, author.name, datepath)
        trackdir = filedir+'trackfile/'

        filehash = filetools.safe_file(trackdir, track_info['name'], track_bin.value)
        gpxtools.parse_gpx(trackdir+track_info['name'])

        track = Track(
                    date = track_info['date'],
                    name = track_info['name'],
                    location = trackdir,
                    hash = filehash,
                    author = author.id,
                    uuid = track_info['uuid'],
                    distance = track_info['distance'],
                    timespan = track_info['timespan'],
                    color = track_info['color']
                    )
        DBSession.add(track)
        DBSession.flush()
        return Response(json.dumps({'item_uuid':track.uuid, 'item_id':track.id, 'log_id':log['id']}))

    else:
        #TODO: So our track is already in the db - why has this not occured in sync?type=status??? 
        print 'ERROR: Track found in DB, but this should have happened in /sync?type=status'
        return Response(json.dumps({'item_uuid':track.uuid, 'item_id':track.id, 'log_id':log['id']}))
    
    return Response(json.dumps({'item_uuid':None, 'item_id':None, 'log_id':log['id']})) #Something went very wrong


@view_config(route_name='sync', request_param='type=parse_track')
def parse_track(request):
   return(bla) 
