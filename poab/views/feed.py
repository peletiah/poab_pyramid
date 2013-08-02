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
    desc,
    and_
)

from poab.helpers.fractions import (
    Fraction
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




@view_config(
    route_name='feed',
    renderer='rss/rss.mako',
)
@view_config(
    route_name='rss',
    renderer='rss/rss.mako',
)
def rss_view(request):
    logs = DBSession.query(Log).order_by(desc(Log.created)).limit(20)
    logdetaillist=list()
    for log in logs:
        twitter = False
        guid = None
        print log.infomarker
        #q = DBSession.query(Trackpoint).filter(Trackpoint.id==log.infomarker)
        #infomarker=q.one()
        ## ###query for last trackpoint
        #q = DBSession.query(Trackpoint).filter(and_(Trackpoint.track_id==infomarker.track_id,Trackpoint.id==infomarker.id)).order_by(asc(Trackpoint.timestamp))
        #lasttrkpt=q.first()
        #q = DBSession.query(Track).filter(Track.id==infomarker.track_id)
        #if q.count() == 1:
        #    track=q.one()
        #    # ###calculate duration from track-info
        #    total_mins = track.timespan.seconds / 60
        #    mins = total_mins % 60
        #    hours = total_mins / 60
        #    timespan = str(hours)+'h '+str(mins)+'min'
        #    rounded_distance=str(track.distance.quantize(Decimal("0.01"), ROUND_HALF_UP))+'km'
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
        try:
            q = DBSession.query(Timezone).filter(Timezone.id==8)
            timezone = q.one()
            localtime=log.created+timezone.utcoffset
        except:
            localtime=log.created
        # ###query for country and continent
        q = DBSession.query(Country).filter(Country.iso_numcode==792)
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
        print '\n\n'
        print imgidtags
        print log.id
        for imgidtag in imgidtags:
                #imageinfo_id=imgidtag[6:-1]
               # print imageinfo_id
               # q = DBSession.query(Imageinfo).filter(Imageinfo.id==imageinfo_id)
               # imageinfo = q.one()
                image_id=re.search("^\[imgid=(\d{1,})\]$",imgidtag).group(1)
                print image_id
                #imageinfo_id=imgidtag[6:-1]
                q = DBSession.query(Image).filter(Image.id==image_id)
                image = q.one()
                #flickrlink_large = 'http://farm%s.static.flickr.com/%s/%s_%s_b.jpg' % (imageinfo.flickrfarm,imageinfo.flickrserver,imageinfo.flickrphotoid,imageinfo.flickrsecret)
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
                log_content_display=log_content_display.replace(imgidtag,inlineimage)
        urlfinder = re.compile('^(http:\/\/\S+)')
        urlfinder2 = re.compile('\s(http:\/\/\S+)')
        def urlify_markdown(value):
            value = urlfinder.sub(r'<\1>', value)
            return urlfinder2.sub(r' <\1>', value)
        log_content_display=markdown.markdown(urlify_markdown(log_content_display))
        class Logdetails(object):
                def __init__(self, topic, twitter, guid, localtime, content, rounded_distance, timezone, timespan, country, continent, lasttrkpt, infomarker, log):
                    self.topic=topic
                    self.twitter=twitter
                    self.guid=guid
                    self.created=localtime.strftime('%Y-%m-%dT%H:%M:%SZ%Z')
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
                    self.location=lasttrkpt.location_ref[0].name
                    self.infomarkerid=log.trackpoint_log_ref.id
                    self.id=log.id
        logdetails = Logdetails(log.topic, twitter, guid, localtime, log_content_display, rounded_distance, timezone, timespan, country, continent, log.trackpoint_log_ref, log.trackpoint_log_ref, log)
        logdetaillist.append(logdetails)
    
    request.response.content_type = "application/atom+xml"
    return {
        'logdetaillist': logdetaillist
    }

