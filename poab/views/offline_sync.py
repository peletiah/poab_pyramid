import hashlib
import json
from json import encoder

from pyramid.response import Response
from pyramid.view import view_config

from poab.models import (
    DBSession,
    Author,
    Etappe,
    Log,
    Track,
    Trackpoint,
    Location,
    Image,
    FlickrImage
)

encoder.FLOAT_REPR = lambda o: format(o, '.2f')

from poab.helpers import (
    timetools,
    imagetools,
    filetools,
    flickrtools
)

from datetime import datetime
import re

@view_config(route_name='sync', request_param='type=status')
def itemstatus(request):
    sync_status='sync_error'
    payload_type = request.POST.get('payloadtype')
    print '\n\n\n\n\n\n\n\n\n\n'
    print payload_type
    print '\n\n\n\n\n\n\n\n\n\n'
    log_json = json.loads(request.POST.get('log_json'))
    if payload_type == 'image':
        image_json = json.loads(request.POST.get('image_json'))
        payload_uuid = image_json['uuid']

        image = Image.get_image_by_uuid(image_json['uuid'])

        if image:
            print 'Image found! '+image.location

            image_bin = open(image.location+image.name, 'rb')
            hash=hashlib.sha256(image_bin.read()).hexdigest()

            if hash == image.hash == image_json['hash']:
                print 'Image already exists on server!'
                sync_status='was_synced'

            else:
                print 'Imagehash mismatch!'
                sync_status='sync_error'
        else:
            sync_status = 'not_synced'
    elif payload_type == 'track':
        track_json = json.loads(request.POST.get('track_json'))
        track = Track.get_track_by_uuid(track_json['uuid'])
        payload_uuid = track_json['uuid']
        if track:
            print 'Track already exists on server!'
            sync_status='was_synced'
        else:
            print 'Track not on server'
            sync_status = 'not_synced'
    return Response(json.dumps({'log_id':log_json['id'],'type':payload_type,  'item_uuid':payload_uuid, 'sync_status':sync_status}))



@view_config(route_name='sync', request_param='type=log')
def logsync(request):
    sync_status='sync_error'
    log_json = json.loads(request.POST.get('log_json').value)
    print log_json
    etappe_json = log_json['etappe']
    #TODO: might be better with dates instead of uuid
    etappe = Etappe.get_etappe_by_uuid(etappe_json['uuid'])
    if not etappe:
        etappe = Etappe(
                start_date = etappe_json['start_date'],
                end_date = etappe_json['end_date'],
                name = etappe_json['name'],
                uuid = etappe_json['uuid']
                )
        DBSession.add(etappe)
        DBSession.flush()

    log = Log.get_log_by_uuid(log_json['uuid'])
    if not log:
        print 'No log found, adding new log.'
        print 'Author: '+log_json['author']
        author = Author.get_author(log_json['author'])
        print author
        log = Log(
                infomarker = None,
                topic=log_json['topic'],
                content=log_json['content'],
                author=author.id,
                etappe=etappe.id,
                created=log_json['created'],
                published=timetools.now(),
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
    return Response(json.dumps({'log_id':log_json['id'], 'type':'log', 'item_uuid':log_json['uuid'], 'sync_status':sync_status}))




@view_config(route_name='sync', request_param='type=image')
def imagesync(request):
    sync_status='sync_error'
    print request.POST.keys()
    image_json = request.POST.get('image_json')
    log_json = json.loads(request.POST.get('log').value)
    image_bin = request.POST.get('image_bin')

    image_json = json.loads(image_json.value)
    author = Author.get_author(image_json['author']['name'])


    image = Image.get_image_by_uuid(image_json['uuid']) #does image with this uuid(from json-info) already exist in our db
    if not image:

        basedir = '/srv/trackdata/bydate'
        img_prvw_w='500'
        img_large_w='990'
        created=datetime.strptime(log_json['created'], "%Y-%m-%d %H:%M:%S") #we use the timestamp from log_json['created'] for the image-location
        datepath=created.strftime("%Y-%m-%d")
        filedir = filetools.createdir(basedir, author.name, datepath)
        imgdir = filedir+'images/sorted/'

        filehash = filetools.safe_file(imgdir, image_json['name'], image_bin.value)

        imagetools.resize(imgdir, imgdir+img_prvw_w+'/', image_json['name'], img_prvw_w)
        imagetools.resize(imgdir, imgdir+img_large_w+'/',image_json['name'] , img_large_w) #TODO: what happens when a 990px-wide img was uploaded?


        hash_large=hashlib.sha256(open(imgdir+img_large_w+'/'+image_json['name'], 'rb').read()).hexdigest() #TODO
        filehash=hashlib.sha256(open(imgdir+'/'+image_json['name'], 'rb').read()).hexdigest() #TODO
        image = Image(
                    name = image_json['name'],
                    location = imgdir,
                    title = image_json['title'],
                    comment = image_json['comment'],
                    alt = image_json['alt'],
                    aperture = image_json['aperture'],
                    shutter = image_json['shutter'],
                    focal_length = image_json['focal_length'],
                    iso = image_json['iso'],
                    timestamp_original = image_json['timestamp_original'],
                    hash = filehash,
                    hash_large = hash_large, #TODO: we need the real file's hash if 990px was uploaded and not converted
                    author = author.id,
                    trackpoint = None,
                    last_change = timetools.now(),
                    published = timetools.now(),
                    uuid = image_json['uuid']
                    )
        DBSession.add(image)
        DBSession.flush()
        sync_status = 'is_synced'

    else:
        #TODO: So our image is actually in the db - why has this been found earlier in sync?type=status???
        print 'ERROR: Image found in DB, but this should have happened in /sync?type=status'
        sync_status='sync_error'

    return Response(json.dumps({'log_id' : log_json['id'], 'type':'image', 'item_uuid':image_json['uuid'], 'sync_status':sync_status})) #Something went very wrong



@view_config(route_name='sync', request_param='type=track')
def tracksync(request):
    sync_status='sync_error'
    print request.POST.keys()
    track_json = json.loads(request.POST.get('track'))
    print track_json['distance']
    log_json = json.loads(request.POST.get('log_json'))
    print '\n'
    print track_json['author']

    author = Author.get_author(track_json['author'])


    track = Track.get_track_by_uuid(track_json['uuid']) #does track with this uuid(from json-info) already exist in our db
    if not track:
        print '\n\n\n'
        print 'Track not found by uuid %s!' %track_json['uuid']
        print '\n\n\n'
        track = Track(
                    reduced_trackpoints = json.loads(track_json['reduced_trackpoints']),
                    distance = track_json['distance'],
                    timespan = track_json['timespan'],
                    trackpoint_count = track_json['trackpoint_count'],
                    start_time = track_json['start_time'],
                    end_time = track_json['end_time'],
                    color = track_json['color'],
                    author = author.id,
                    etappe = None,
                    uuid = track_json['uuid']
                    )
        DBSession.add(track)
        DBSession.flush()
        for trackpoint_json in track_json['trackpoints']:
            trackpoint_in_db = Trackpoint.get_trackpoint_by_lat_lon_time(trackpoint_json['latitude'], \
                                        trackpoint_json['longitude'], trackpoint_json['timestamp'])
            if not trackpoint_in_db:
                print trackpoint_json
                trackpoint = Trackpoint(
                                    track_id = track.id,
                                    latitude = trackpoint_json['latitude'],
                                    longitude = trackpoint_json['longitude'],
                                    altitude = trackpoint_json['altitude'],
                                    velocity = trackpoint_json['velocity'],
                                    temperature = trackpoint_json['temperature'],
                                    direction = trackpoint_json['direction'],
                                    pressure = trackpoint_json['pressure'],
                                    timestamp = trackpoint_json['timestamp'],
                                    uuid = trackpoint_json['uuid']
                                    )
                DBSession.add(trackpoint)
                DBSession.flush()

        sync_status = 'is_synced'

    elif track:
        print 'was_synced'
        sync_status = 'was_synced'
    else:
        print 'sync_error'
        sync_status = 'sync_error'

    return Response(json.dumps({'log_id':log_json['id'], 'type':'track', 'item_uuid':track_json['uuid'], 'sync_status':sync_status}))

@view_config(route_name='sync', request_param='interlink=log')
def interlink_log(request):
    log_json =  json.loads(request.POST.get('log_json'))
    log = Log.get_log_by_uuid(log_json['uuid'])
    latest_timestamp = datetime.strptime('1970-01-01', '%Y-%m-%d')
    #Link to Tracks
    for track in log_json['tracks']:
        track = Track.get_track_by_uuid(track['uuid'])
        print '############### track.id #########'
        print track.id
        print '################ track.id end #########'
        log.track.append(track)
        #find the latest trackpoint-timestamp related to this log
        #this will be the trackpoint linked to log as infomarker
        if track.trackpoints[0].timestamp > latest_timestamp:
            log.infomarker = track.trackpoints[0].id
            latest_timestamp = track.trackpoints[0].timestamp
    print log_json['tracks']
    if not log_json['tracks']:
        log.infomarker = 3572 #TODO

    #Get location for infomarker
    location = Location(name = None, trackpoint_id = None, country_id = None)
    location.name = flickrtools.findplace(log.trackpoint_log_ref.latitude, log.trackpoint_log_ref.longitude, 11, log.author_log_ref)
    location.trackpoint_id = log.trackpoint_log_ref.id,
    location.country_id = flickrtools.get_country_by_lat_lon(log.trackpoint_log_ref.latitude, log.trackpoint_log_ref.longitude, log.author_log_ref).iso_numcode
    #print '\n\n\n\n\n\n'+location.name
    print '\n\n\n\n\n'
    DBSession.add(location)

    #Link to Images
    for image in log_json['images']:
        image = Image.get_image_by_uuid(image['uuid'])
        log.image.append(image)

    content_with_uuid_tags = log.content
    #print content_with_uuid_tags
    img_uuid_list = re.findall("(\[img_uuid=[0-9A-Za-z-]{1,}\])", content_with_uuid_tags)
    #regex matches A-Z, a-z, 0-9 and "-", e.g. "0eb92a91-3a92-4707-be6e-1907f6c0829"
    print img_uuid_list
    for img_uuid_tag in img_uuid_list:
        img_uuid = re.search("^\[img_uuid=([0-9A-Za-z-]{1,})\]$",img_uuid_tag).group(1)
        image = Image.get_image_by_uuid(img_uuid)
        if image:
            content_with_uuid_tags=content_with_uuid_tags.replace(img_uuid_tag,('[imgid=%s]') % image.id)
    log.content = content_with_uuid_tags
    DBSession.add(log)
    return Response(json.dumps({'link_status':'linked', 'item_uuid': log.uuid}))



@view_config(route_name='sync', request_param='interlink=image')
def interlink_image(request):
    image_json = json.loads(request.POST.get('image_json'))
    print image_json['id']
    print image_json['name']
    print image_json['trackpoint']
    image = Image.get_image_by_uuid(image_json['uuid'])
    try:
        trackpoint = Trackpoint.get_trackpoint_by_uuid(image_json['trackpoint']['uuid'])
    except:
        trackpoint = None
    location = None
    if trackpoint:
        print trackpoint
        print image
        image.trackpoint = trackpoint.id
    #Get location for image.trackpoint
        location = Location(name = None, trackpoint_id = None, country_id = None)
        location.name = flickrtools.findplace(image.trackpoint_img_ref.latitude, image.trackpoint_img_ref.longitude, 11, image.author_img_ref)
        location.trackpoint_id = image.trackpoint_img_ref.id,
        location.country_id = flickrtools.get_country_by_lat_lon(image.trackpoint_img_ref.latitude, image.trackpoint_img_ref.longitude, image.author_img_ref).iso_numcode
    if not image.image_flickr_ref:
        print '\n\n\n\n\n\n\n'+str(image.id)
        print '\n\n\n\n\n\n\n'
        farm,server,photoid,secret,originalsecret,originalformat = flickrtools.uploadimage(image, image.author_img_ref, '')
        flickrimage = FlickrImage(image = image.id, farm = farm, server = server, photoid = photoid, secret = secret)
        DBSession.add(flickrimage)
    DBSession.add(image)
    if location: #TODO(Ugly?)
        DBSession.add(location)


    return Response(json.dumps({'link_status':'linked', 'item_uuid': image.uuid}))




@view_config(route_name='sync', request_param='interlink=track')
def interlink_track(request):
    track_json = json.loads(request.POST.get('track_json'))
    print track_json['id']
    print track_json['start_time']
    track = Track.get_track_by_uuid(track_json['uuid'])
    etappen = Etappe.get_etappen_by_date(track_json['start_time'])
    print etappen
    for etappe in etappen:
        print etappe.start_date
        etappe.track.append(track)
    return Response(json.dumps({'link_status':'linked', 'item_uuid': track.uuid}))


