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
    Imageinfo,
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
        print log.infomarker_id
        q = DBSession.query(Trackpoint).filter(Trackpoint.id==log.infomarker_id)
        infomarker=q.one()
        # ###query for last trackpoint
        q = DBSession.query(Trackpoint).filter(and_(Trackpoint.track_id==infomarker.track_id,Trackpoint.id==infomarker.id)).order_by(asc(Trackpoint.timestamp))
        lasttrkpt=q.first()
        q = DBSession.query(Track).filter(Track.id==infomarker.track_id)
        if q.count() == 1:
            track=q.one()
            # ###calculate duration from track-info
            total_mins = track.timespan.seconds / 60
            mins = total_mins % 60
            hours = total_mins / 60
            timespan = str(hours)+'h '+str(mins)+'min'
            rounded_distance=str(track.distance.quantize(Decimal("0.01"), ROUND_HALF_UP))+'km'
        else:
            rounded_distance=None
            timespan=None
        # ###query for timezone and calculate localtime
        q = DBSession.query(Timezone).filter(Timezone.id==infomarker.timezone_id)
        try:
            timezone = q.one()
            localtime=log.created+timezone.utcoffset
        except:
            localtime=log.created
        # ###query for country and continent
        q = DBSession.query(Country).filter(Country.iso_numcode==infomarker.country_id)
        country=q.one()
        q = DBSession.query(Continent).filter(Continent.id==country.continent_id)
        continent=q.one()
        p=re.compile("http://twitter.com/derreisende/statuses/(?P<guid>\d{1,})")
        if p.search(log.topic):
            guid=p.search(log.topic).group("guid")
            twitter=True
        log_bla=log.content
        imgidtags=re.findall('\[imgid[0-9]*\]',log_bla)
        print imgidtags
        print log.id
        for imgidtag in imgidtags:
                imageinfo_id=imgidtag[6:-1]
                print imageinfo_id
                q = DBSession.query(Imageinfo).filter(Imageinfo.id==imageinfo_id)
                imageinfo = q.one()
                #flickrlink_large = 'http://farm%s.static.flickr.com/%s/%s_%s_b.jpg' % (imageinfo.flickrfarm,imageinfo.flickrserver,imageinfo.flickrphotoid,imageinfo.flickrsecret)
                image_large = '/static%s' % (imageinfo.imgname)
                if imageinfo.flickrdescription==None:
                    inlineimage='''<div class="log_inlineimage"> <div class="imagecontainer"><a href="%s" title="%s" rel="image_colorbox"><img class="inlineimage" src="http://farm%s.static.flickr.com/%s/%s_%s.jpg" alt="%s" /></a><div class="caption">
        <span>&#8594;</span>
            <a href="http://www.flickr.com/peletiah/%s" target="_blank">www.flickr.com</a>
    </div></div></div>''' % (image_large,imageinfo.flickrtitle,imageinfo.flickrfarm,imageinfo.flickrserver,imageinfo.flickrphotoid,imageinfo.flickrsecret,imageinfo.flickrtitle,imageinfo.flickrphotoid)
                else:
                    inlineimage='''<div class="log_inlineimage"><div class="imagecontainer"><a href="%s" title="%s" rel="image_colorbox" ><img class="inlineimage" src="http://farm%s.static.flickr.com/%s/%s_%s.jpg" alt="%s" /></a><div class="caption">
        <span>&#8594;</span>
            <a href="http://www.flickr.com/peletiah/%s" target="_blank">www.flickr.com</a>
    </div></div><span class="imagedescription">%s</span></div>''' % (image_large,imageinfo.flickrtitle,imageinfo.flickrfarm,imageinfo.flickrserver,imageinfo.flickrphotoid,imageinfo.flickrsecret,imageinfo.flickrtitle,imageinfo.flickrphotoid,imageinfo.flickrdescription)

                log_bla=log_bla.replace(imgidtag,inlineimage)
        urlfinder = re.compile('^(http:\/\/\S+)')
        urlfinder2 = re.compile('\s(http:\/\/\S+)')
        def urlify_markdown(value):
            value = urlfinder.sub(r'<\1>', value)
            return urlfinder2.sub(r' <\1>', value)
        log_bla=markdown.markdown(urlify_markdown(log_bla))
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
                    self.location=lasttrkpt.location
                    self.infomarkerid=infomarker.id
                    self.id=log.id
        logdetails = Logdetails(log.topic, twitter, guid, localtime, log_bla, rounded_distance, timezone, timespan, country, continent, lasttrkpt, infomarker, log)
        logdetaillist.append(logdetails)
    
    request.response.content_type = "application/atom+xml"
    return {
        'logdetaillist': logdetaillist
    }

