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

from poab.helpers.timetools import (
    timediff
)

import markdown

from decimal import Decimal, ROUND_HALF_UP

from poab.models import (
    DBSession,
    Log,
    Track,
    Trackpoint,
    Image,
    Timezone,
    Country,
    Continent
    )

import re

def fetch_images_for_trackpoints(q):
    trackpoints = q.all()
    trkpt_list=list()
    for trackpoint in trackpoints:
        trkpt_list.append(trackpoint.id)
    q = DBSession.query(Image).filter(and_(Image.trackpoint.in_(trkpt_list)))
    images = q.order_by(asc(Image.timestamp_original)).all()
    return images



@view_config(
    route_name='view',
    renderer='/view/view.mako',
)

@view_config(
    route_name='view:action',
    renderer='/view/view.mako',
)
def view_view(request):
    try:
        action=request.matchdict['action']
    except:
        action='c'
    try:
        id=int(request.matchdict['id'])
    except:
        id=0
    try:
        page_number=int(request.matchdict['page'].replace('/',''))
    except:
        page_number=None
    if id==0 and page_number==None:
        q = DBSession.query(Image)
        image_count=q.count()
        page_fract=float(Fraction(str(image_count)+'/10'))
        if int(str(page_fract).split('.')[1])==0:
            page=int(str(page_fract).split('.')[0])-1
        else:               
            page=str(page_fract).split('.')[0]
    elif page_number==None:
        page=0
    else:
        page=page_number
    #navstring=countryDetails(model,id)
    curr_page=int(page)
    #return { 'bla': log_count}
    if id==0:
        ##TODO what was the idea behind "country_id!=None"?
        ##q = DBSession.query(Trackpoint).filter(Trackpoint.country_id!=None)
        q = DBSession.query(Trackpoint)
        images=fetch_images_for_trackpoints(q)
        print '\n\n\n\n\n'
        print images
        print '\n\n\n\n\n'
    elif action=='c':
        q = DBSession.query(Trackpoint).filter(and_(Trackpoint.country_id==id))
        images=fetch_images_for_trackpoints(q)
    elif action=='infomarker':
        q = DBSession.query(Trackpoint).filter(and_(Trackpoint.id==id))
        images=fetch_images_for_trackpoints(q)
    elif action=='id':
        images = DBSession.query(Image).filter(Image.id==id).all()
    page_list=list()
    pages_list=list()
    i=0
    for image in images:
        page_list.append(image)
        i=i+1
        if i==10:
            page_list.reverse()
            pages_list.append(page_list)
            page_list=list()
            i=0
    if i<10 and i>0:
        page_list.reverse()
        pages_list.append(page_list)
    viewlist=list()
    for image in pages_list[curr_page]:
        if image.trackpoint:
            trackpoint_id=image.trackpoint
        else:
            trackpoint_id=image.infomarker_id
            prefix='near '
        q = DBSession.query(Trackpoint).filter(Trackpoint.id==trackpoint_id)
        trackpointinfo=q.one()
        ##TODO: fix timezone
        ##q = DBSession.query(Timezone).filter(Timezone.id==trackpointinfo.timezone_id)
        q = DBSession.query(Timezone).filter(Timezone.id==8)
        timezone = q.one()
        localtime = image.timestamp_original+timezone.utcoffset
        deltaseconds=round(timezone.utcoffset.days*86400+timezone.utcoffset.seconds)
        #TODO THIS SUCKS!
        class Viewdetail(object):
            def __init__(self, photoid, title, description, log_id, imgname, aperture, shutter, focal_length, iso, trackpointinfo, localtime, timezone, utcoffset):
                self.photoid=photoid
                self.title=title
                self.description=description
                self.log_id=log_id
                self.name = image.name
                self.aperture= image.aperture
                self.shutter= image.shutter
                self.focal_length= image.focal_length
                self.iso= image.iso
                #logdate=c.loginfo.created.strftime('%Y-%m-%d') #needed for the imagepath
                self.trackpointinfo=trackpointinfo
                self.localtime=localtime
                self.timezone=timezone
                #calculate the offset in seconds
                self.utcoffset=utcoffset
        viewdetail = Viewdetail(image.id, image.flickrfarm, image.flickrserver, image.flickrphotoid, image.flickrsecret, image.flickrtitle, image.flickrdescription, image.log_id, image.imgname, image.aperture, image.shutter, image.focal_length, image.iso, trackpointinfo, localtime.strftime('%Y-%m-%d %H:%M:%S'), timezone, timediff(deltaseconds))
        viewlist.append(viewdetail)

    return {
        'pages_list': pages_list,
        'curr_page': int(curr_page),
        'viewlist': viewlist,
        'request': request,
        'action': action,
        'id': id,
    }

