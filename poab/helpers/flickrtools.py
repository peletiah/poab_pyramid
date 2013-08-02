import flickrapi

from poab.models  import (
    DBSession,
    Author,
    FlickrCredentials,
    Country
    )

from lxml import etree

def getcredentials(author):
    credentials=FlickrCredentials.get_flickrcredentials_by_author(author.id)
    flickr = flickrapi.FlickrAPI(credentials.api_key, credentials.api_secret, username=author.name, format='etree')
    return flickr


def getimginfo(photoid, author):
    try:
        credentials=FlickrCredentials.get_flickrcredentials_by_author(author.id)
        flickr = flickrapi.FlickrAPI(credentials.api_key, credentials.api_secret, username=author.name, format='etree')

        photoinfo=flickr.photos_getInfo(photo_id=photoid)
        secret=photoinfo.find('photo').attrib['secret']
        originalsecret=photoinfo.find('photo').attrib['originalsecret']
        server=photoinfo.find('photo').attrib['server']
        farm=photoinfo.find('photo').attrib['farm']
        originalformat=photoinfo.find('photo').attrib['originalformat']
        return farm,server,photoid,secret,originalsecret,originalformat
    except flickrapi.FlickrError, (value):
        sys.stderr.write("%s\n" % (value, ))
        sys.exit(1)



def uploadimage(image, author, size):
    credentials=FlickrCredentials.get_flickrcredentials_by_author(author.id)
    flickr = flickrapi.FlickrAPI(credentials.api_key, credentials.api_secret, username=author.name, format='etree')
    
    filename = str(image.location+size+image.name)
    title = image.title
    if not title:
        title = ''
    description = image.comment
    if not description:
        description = ''
    tags = ''
    print '\n\n\n\n'
    print image.id
    print title.encode('utf-8'), description.encode('utf-8')
    print '\n\n\n\n'
    result=flickr.upload(filename=str(filename),title=title,description=description,tags=tags)
    photoid = result.find('photoid').text
    farm,server,photoid,secret,originalsecret,originalformat = getimginfo(photoid, author)
    return farm,server,photoid,secret,originalsecret,originalformat


def findplace(lat,lon,accuracy, author):
    flickr = getcredentials(author)
    try:
        place=flickr.places_findByLatLon(lat=lat,lon=lon,accuracy=accuracy)
        try:
            name=place.find('places/place').attrib['name']
            #place_id=place.find('places/place').attrib['place_id']
            if name==None:
                name='Here be dragons'
            return name
        except AttributeError:
            return 'Here be dragons'
    except flickrapi.FlickrError, (value):
        sys.stderr.write("%s\n" % (value, ))
        sys.exit(1)

def get_country_by_lat_lon(lat,lon,author):
    accuracy=1 #level of region-detail in flickr, 1 is world, 8 is district
    flickr_countryname=findplace(lat,lon,accuracy,author)
    print "flickr_countryname: "+str(flickr_countryname)
    if flickr_countryname !=None:
        country=DBSession.query(Country).filter(Country.flickr_countryname==flickr_countryname).one()
        print 'country found - id:'+ str(country.iso_numcode) + ' - details:' + str(country)
    else:
        print "no country found, returning dummy country!"
        query_country=session.query(db_country).filter(db_country.iso_numcode==1)
        country=query_country.one()
    return country
    
    
    
    
