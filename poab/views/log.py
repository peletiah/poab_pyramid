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

from poab.helpers import flickrtools

import markdown

from decimal import Decimal, ROUND_HALF_UP

from poab.models import (
    DBSession,
    Log,
    Track,
    Trackpoint,
    Location,
    Image,
    Imageinfo,
    Timezone,
    Country,
    Continent
    )

import re


@view_config(
    route_name='home'
)
def home(request):
    raise HTTPFound(request.route_url("log"))



def get_logs_by_trackpoints(trackpoints):
    trkpt_list=list()
    for trackpoint in trackpoints:
        trkpt_list.append(trackpoint.id)
    q = DBSession.query(Log).filter(and_(Log.infomarker_id.in_(trkpt_list),Log.id!=29))
    logs = q.order_by(asc(Log.created)).all()
    return logs




@view_config(
    route_name='log',
    renderer='log/log.mako',
)
@view_config(
    route_name='log:action',
    renderer='log/log.mako',
)
def log_view(request):
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
        q = DBSession.query(Log).order_by(Log.created)
        log_count = q.count()
        page_fract=float(Fraction(str(log_count)+'/3'))
        print '\n\n\n PAGE FRACT'
        print page_fract
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
    if action=='c' and id==0:
        #TODO do we really want to query all logs here?
        ##trackpoints = DBSession.query(Trackpoint).filter(Trackpoint.infomarker==True).all()
        ##country_id=id
        ##logs=get_logs_by_trackpoints(trackpoints)
        logs = DBSession.query(Log).order_by(Log.created).all()
    elif action=='c':
        locations = DBSession.query(Location).filter(Location.country_id==id).all()
        trackpoints = list()
        for location in locations:
            trackpoint = DBSession.query(Trackpoint).filter(Trackpoint.location_ref.contains(location)).all()
            trackpoints.append(trackpoint)
        logs = list()
        for trackpoint in trackpoints:
            print trackpoint
            log = DBSession.query(Log).filter(Log.trackpoint_log_ref==trackpoint).all()
            logs.append(log)            
    elif action=='id': 
        logs = DBSession.query(Log).filter(Log.id==id).order_by(Log.created).all()
    page_list=list()
    pages_list=list()
    i=0
    for log in logs:
        page_list.append(log)
        i=i+1
        if i==3:
            page_list.reverse()
            pages_list.append(page_list)
            page_list=list()
            i=0
    if i<3 and i>0:
        page_list.reverse()
        pages_list.append(page_list)
    logdetaillist=list()
    for log in pages_list[curr_page]:
        twitter = False
        guid = None
        print log.trackpoint_log_ref
        # ###query for last trackpoint
        ##q = DBSession.query(Trackpoint).filter(and_(Trackpoint.track_id==infomarker.track_id,Trackpoint.id==infomarker.id)).order_by(asc(Trackpoint.timestamp))
        ##lasttrkpt=q.first()
        # ###query if images exist for the log
        print log.images
        if len(log.images) > 0:
            #creates the infomarker-image_icon-and-ajax-link(fancy escaping for js needed):
            gallerylink="""<span class="image_icon"><a title="Show large images related to this entry" href="/view/log/%s/0"></a></span>""" % (log.id)
        else:
            gallerylink=''
        print log.tracks
        if len(log.tracks) > 0:
            # ###calculate duration from track-info
            total_seconds = 0
            total_distance = Decimal(0)
            for track in log.tracks:
                total_seconds = total_seconds + track.timespan.seconds
                total_distance = total_distance + Decimal(track.distance)
            total_minutes = total_seconds / 60
            mins = total_minutes % 60 #full minutes left after division by 60
            hours = total_minutes / 60
            timespan = str(hours)+'h '+str(mins)+'min'
            rounded_distance=str(total_distance.quantize(Decimal("0.01"), ROUND_HALF_UP))+'km'
            print timespan, rounded_distance
        else:
            rounded_distance=None
            timespan=None
        # ###query for timezone and calculate localtime
        try:#TODO: fix timezone querying
            ##q = DBSession.query(Timezone).filter(Timezone.id==infomarker.timezone_id)
            q = DBSession.query(Timezone).filter(Timezone.id==8) #TODO: EEST for testing only
            timezone = q.one()
            localtime=log.created+timezone.utcoffset
        except:
            localtime=log.created
        ## ###query for country and continent #TODO
        #q = DBSession.query(Country).filter(Country.iso_numcode==infomarker.country_id)
        q = DBSession.query(Country).filter(Country.iso_numcode==792) #TODO Turkey for testing only
        country=q.one()
        q = DBSession.query(Continent).filter(Continent.id==country.continent_id)
        continent=q.one()
        p=re.compile("http://twitter.com/derreisende/statuses/(?P<guid>\d{1,})")
        if p.search(log.topic):
            guid=p.search(log.topic).group("guid")
            twitter=True
        log_content_display=log.content
        imgidtags=re.findall('\[imgid=[0-9]*\]',log_content_display)
        print '\n\n'
        print imgidtags
        for imgidtag in imgidtags:
                print imgidtag
                image_id=re.search("^\[imgid=(\d{1,})\]$",imgidtag).group(1)
                print image_id
                #imageinfo_id=imgidtag[6:-1]
                q = DBSession.query(Image).filter(Image.id==image_id)
                image = q.one()
                print image
                print '\n\n'
                print '\n\n'
                print image.location
                print '\n\n'
                print '\n\n'
                if image.comment:
                    inlineimage='''<div class="log_inlineimage"><div class="imagecontainer"><a href="%s%s%s" title="%s" rel="image_colorbox"><img class="inlineimage" src="%s%s%s%s" alt="%s" /></a><div class="caption">
        <span>&#8594;</span>
            <a href="http://www.flickr.com/peletiah/%s" target="_blank">www.flickr.com</a>
    </div></div><span class="imagedescription">%s</span></div>''' % ('/static', image.location.replace('/srv',''), image.name, image.title, '/static', image.location.replace('/srv',''), '500/', image.name, image.alt, image.image_flickr_ref[0].photoid, image.comment)
                else:
                    inlineimage='''<div class="log_inlineimage"><div class="imagecontainer"><a href="%s%s%s" title="%s" rel="image_colorbox" ><img class="inlineimage" src="%s%s%s%s" alt="%s" /></a><div class="caption">
        <span>&#8594;</span>
            <a href="http://www.flickr.com/peletiah/%s" target="_blank">www.flickr.com</a>
    </div></div></div>''' % ('/static', image.location.replace('/srv',''), image.name, image.title, '/static', image.location.replace('/srv',''), '500/', image.name, image.alt, image.image_flickr_ref[0].photoid) #TODO breaks when no flickr-info in db

                #flickrlink_large = 'http://farm%s.static.flickr.com/%s/%s_%s_b.jpg' % (imageinfo.flickrfarm,imageinfo.flickrserver,imageinfo.flickrphotoid,imageinfo.flickrsecret)
                ##image_large = '/static%s' % (imageinfo.imgname) #TODO from flickr or local?
                ##if imageinfo.flickrdescription==None:
                    ##inlineimage='''<div class="log_inlineimage"> <div class="imagecontainer"><a href="%s" title="%s" rel="image_colorbox"><img class="inlineimage" src="http://farm%s.static.flickr.com/%s/%s_%s.jpg" alt="%s" /></a><div class="caption">
        ##<span>&#8594;</span>
        ##    <a href="http://www.flickr.com/peletiah/%s" target="_blank">www.flickr.com</a>
   ## </div></div></div>''' % (image_large,imageinfo.flickrtitle,imageinfo.flickrfarm,imageinfo.flickrserver,imageinfo.flickrphotoid,imageinfo.flickrsecret,imageinfo.flickrtitle,imageinfo.flickrphotoid)
                ##else:
                    ##inlineimage='''<div class="log_inlineimage"><div class="imagecontainer"><a href="%s" title="%s" rel="image_colorbox" ><img class="inlineimage" src="http://farm%s.static.flickr.com/%s/%s_%s.jpg" alt="%s" /></a><div class="caption">
        ##<span>&#8594;</span>
        ##    <a href="http://www.flickr.com/peletiah/%s" target="_blank">www.flickr.com</a>
    ##</div></div><span class="imagedescription">%s</span></div>''' % (image_large,imageinfo.flickrtitle,imageinfo.flickrfarm,imageinfo.flickrserver,imageinfo.flickrphotoid,imageinfo.flickrsecret,imageinfo.flickrtitle,imageinfo.flickrphotoid,imageinfo.flickrdescription)

                log_content_display=log_content_display.replace(imgidtag,inlineimage)
        urlfinder = re.compile('^(http:\/\/\S+)')
        urlfinder2 = re.compile('\s(http:\/\/\S+)')
        def urlify_markdown(value):
            value = urlfinder.sub(r'<\1>', value)
            return urlfinder2.sub(r' <\1>', value)
        log_content_display=markdown.markdown(urlify_markdown(log_content_display))
        class Logdetails(object):
                def __init__(self, topic, twitter, guid, localtime, content, rounded_distance, timezone, timespan, country, continent, lasttrkpt, infomarker, log, gallerylink):
                    self.topic=topic
                    self.twitter=twitter
                    self.guid=guid
                    self.created=localtime.strftime('%B %d, %Y')
                    self.content=content
                    try:
                        self.distance=rounded_distance
                    except NameError:
                        self.distance='-'
                    self.timezoneabbriv=timezone.abbreviation
                    if timespan:
                        self.timespan=timespan
                    else:
                        self.timespan=None
                    self.country=country.iso_countryname
                    self.continent=continent.name
                    self.location=log.trackpoint_log_ref.location_ref[0].name
                    self.infomarkerid=log.trackpoint_log_ref.id
                    self.id=log.id
                    self.gallerylink=gallerylink
        logdetails = Logdetails(log.topic, twitter, guid, localtime, log_content_display, rounded_distance, timezone, timespan, country, continent, log.trackpoint_log_ref, log.trackpoint_log_ref, log, gallerylink) #TODO: "log.trackpoint_log_ref, log.trackpoint_log_ref" was originally "infomarker, lasttrkpt"
        logdetaillist.append(logdetails)

    return {
        'pages_list': pages_list,
        'curr_page': int(curr_page),
        'logdetaillist': logdetaillist,
        'request': request,
        'action': action,
        'id': id,
        'country': country
    }



@view_config(
    route_name='svg',
    renderer='misc/country_svg.mako',
)
def svg_view(request):
    country_id=int(request.matchdict['country_id'])
    if country_id==0:
            return {'country': 'world'}
    q = DBSession.query(Country).filter(Country.iso_numcode==country_id)
    country=q.one()
    return {'country': country.iso_numcode}

