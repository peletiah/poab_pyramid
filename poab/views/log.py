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
    route_name='home'
)
def home(request):
    raise HTTPFound(request.route_url("log"))



def get_logs_by_trackpoints(trackpoints):
    trkpt_list=list()
    for trackpoint in trackpoints:
        trkpt_list.append(trackpoint.id)
    q = DBSession.query(Log).filter(and_(Log.infomarker_id.in_(trkpt_list)))
    logs = q.order_by(asc(Log.createdate)).all()
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
        q = DBSession.query(Log)#.filter(model.log.createdate>=older_createdate)
        log_count = q.count()
        page_fract=float(Fraction(str(log_count)+'/3'))
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
        trackpoints = DBSession.query(Trackpoint).filter(Trackpoint.infomarker==True).all()
        country_id=id
        logs=get_logs_by_trackpoints(trackpoints)
    elif action=='c':
        trackpoints = DBSession.query(Trackpoint).filter(and_(Trackpoint.country_id==id,Trackpoint.infomarker==True)).all()
        country_id=id
        logs=get_logs_by_trackpoints(trackpoints)
    elif action=='id': 
        logs = DBSession.query(Log).filter(Log.id==id).all()
        country_id = DBSession.query(Trackpoint).filter(Trackpoint.id==logs[0].infomarker_id).one().country_id
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
        q = DBSession.query(Trackpoint).filter(Trackpoint.id==log.infomarker_id)
        infomarker=q.one()
        # ###query for last trackpoint
        q = DBSession.query(Trackpoint).filter(and_(Trackpoint.track_id==infomarker.track_id,Trackpoint.id==infomarker.id)).order_by(asc(Trackpoint.timestamp))
        lasttrkpt=q.first()
        # ###query if images exist for the log
        q = DBSession.query(Imageinfo).filter(Imageinfo.infomarker_id==infomarker.id)
        if q.count() > 0:
            #creates the infomarker-image_icon-and-ajax-link(fancy escaping for js needed):
            gallerylink="""<span class="image_icon"><a title="Show large images related to this entry" href="/view/infomarker/%s/0"></a></span>""" % (infomarker.id)
        else:
            gallerylink=''
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
            localtime=log.createdate+timezone.utcoffset
        except:
            localtime=log.createdate
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
        for imgidtag in imgidtags:
                imageinfo_id=imgidtag[6:-1]
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
                def __init__(self, topic, twitter, guid, localtime, content, rounded_distance, timezone, timespan, country, continent, lasttrkpt, infomarker, log, gallerylink):
                    self.topic=topic
                    self.twitter=twitter
                    self.guid=guid
                    self.createdate=localtime.strftime('%B %d, %Y')
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
                    self.gallerylink=gallerylink
        logdetails = Logdetails(log.topic, twitter, guid, localtime, log_bla, rounded_distance, timezone, timespan, country, continent, lasttrkpt, infomarker, log, gallerylink)
        logdetaillist.append(logdetails)

    return {
        'pages_list': pages_list,
        'curr_page': int(curr_page),
        'logdetaillist': logdetaillist,
        'request': request,
        'action': action,
        'id': id,
        'country_id': country_id
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

