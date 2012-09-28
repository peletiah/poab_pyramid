from sqlalchemy import (
    ForeignKey,
    Column,
    Integer,
    Text,
    types,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

import datetime

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

def now():
    return datetime.datetime.now()

class Log(Base):
    __tablename__ = 'log'
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    infomarker_id = Column("infomarker_id", types.Integer, ForeignKey('trackpoint.id'))
    topic = Column("topic", types.UnicodeText)
    content = Column("content", types.UnicodeText)
    createdate = Column("createdate", types.TIMESTAMP(timezone=False),default=now())

    def __init__(self, topic, content, createdate):
        self.infomarker_id = infomarker_id
        self.topic = topic
        self.content = content
        self.createdate = createdate

class Track(Base):
    __tablename__ = 'track'
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    date = Column("date", types.TIMESTAMP(timezone=False))
    trkptnum = Column("trkptnum", Integer)
    distance = Column("distance", types.Numeric(11,4))
    timespan = Column("timespan", types.Interval)
    gencpoly_pts = Column("gencpoly_pts", types.UnicodeText)
    gencpoly_levels = Column("gencpoly_levels", types.UnicodeText)
    color = Column("color", types.CHAR(6), default='FF0000')
    maxlat = Column("maxlat", types.Numeric(9,7))
    maxlon = Column("maxlon", types.Numeric(10,7))
    minlat = Column("minlat", types.Numeric(9,7))
    minlon = Column("minlon", types.Numeric(10,7))
    json_0002 = Column("json_0002", Text)

    def __init__(self, date, trkptnum, distance, timespan, gencpoly_pts, gencpoly_levels, color, maxlat, maxlon, minlat, minlon, json_0002):
        self.date = date
        self.trkptnum = trkptnum
        self.distance = distance
        self.timespan = timespan
        self.gencpoly_pts = gencpoly_pts
        self.gencpoly_levels = gencpoly_levels
        self.color = color
        self.maxlat = maxlat
        self.maxlon = maxlon
        self.minlat = minlat
        self.minlon = minlon
        self.json_0002 = json_0002


class Imageinfo(Base):
    __tablename__ = 'imageinfo'
    id = Column("id", types.Integer, primary_key=True, autoincrement=True)
    log_id = Column("log_id", types.Integer, ForeignKey('log.id'))
    #photoset_id = Column("photoset_id", types.Integer, ForeignKey('photosets.id'))
    infomarker_id = Column("infomarker_id", types.Integer, ForeignKey('trackpoint.id'))
    trackpoint_id = Column("trackpoint_id", types.Integer, ForeignKey('trackpoint.id'))
    flickrfarm = Column("flickrfarm", types.VARCHAR(256))
    flickrserver = Column("flickrserver", types.VARCHAR(256))
    flickrphotoid = Column("flickrphotoid", types.VARCHAR(256))
    flickrsecret = Column("flickrsecret", types.VARCHAR(256))
    flickrdatetaken = Column("flickrdatetaken", types.TIMESTAMP(timezone=False))
    flickrtitle = Column("flickrtitle", types.VARCHAR(256))
    flickrdescription = Column("flickrdescription", types.UnicodeText)
    photohash = Column("photohash", types.VARCHAR(256))
    photohah_990 = Column("photohash_990", types.VARCHAR(256))
    imgname = Column("imgname", types.VARCHAR(128))
    aperture = Column("aperture", types.VARCHAR(8))
    shutter = Column("shutter", types.VARCHAR(64))
    focal_length = Column("focal_length", types.VARCHAR(64))
    iso = Column("iso", types.VARCHAR(8))
    online = Column("online", types.Boolean, default=False, nullable=False)
    fullsize_online = Column("fullsize_online", types.Boolean, default=False, nullable=False)


    def __init__(self, flickrfarm, flickrserver, flickrphotoid, flickrsecret, flickrdatetaken, flickrtitle, flickrdescription):
        self.flickrfarm = flickrfarm
        self.flickrserver = flickrserver
        self.flickrphotoid = flickrphotoid
        self.flickrsecret = flickrsecret
        self.flickrdatetaken = flickrdatetaken
        self.flickrtitle = flickrtitle
        self.flickrdescription = flickrdescription


class Trackpoint(Base):
    __tablename__ = 'trackpoint'
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    track_id = Column("track_id", types.Integer, ForeignKey('track.id'))
    timezone_id = Column("timezone_id", types.Integer, ForeignKey('timezone.id'))
    country_id = Column("country_id", types.Integer, ForeignKey('country.iso_numcode'))
    latitude = Column("latitude", types.Numeric(9,7))
    longitude = Column("longitude", types.Numeric(10,7))
    altitude = Column("altitude", types.Integer)
    velocity = Column("velocity", types.Integer)
    temperature = Column("temperature", types.Integer)
    direction = Column("direction", types.Integer)
    pressure = Column("pressure", types.Integer)
    timestamp = Column("timestamp", types.TIMESTAMP(timezone=False))
    infomarker = Column("infomarker", types.Boolean, default=False, nullable=False)
    location = Column("location", types.VARCHAR(256))

    def __init__(self, track_id, timezone_id, country_id, latitude, longitude, altitude, velocity, temperature, direction, pressure, timestamp, infomarker, location):
        self.track_id = track_id
        self.timezone_id = timezone_id
        self.country_id = country_id
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.velocity = velocity
        self.temperature = temperature
        self.direction = direction
        self.pressure = pressure
        self.timestamp = timestamp
        self.informarker = infomarker
        self.location = location

class Timezone(Base):
    __tablename__ = 'timezone'
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    utcoffset = Column("utcoffset", types.Interval)
    abbreviation = Column("abbreviation", types.VARCHAR(256))
    description = Column("description", types.VARCHAR(256))
    region = Column("region", types.VARCHAR(256))


    def __init__(self, utcoffset, abbreviation, description, region):
        self.utcoffset = utcoffset
        self.abbreviation = abbreviation
        self.description = description
        self.region = region


class Country(Base):
    __tablename__ = 'country'
    iso_numcode = Column("iso_numcode", types.Integer, primary_key=True)
    continent_id = Column("continent_id", types.Integer, ForeignKey('continent.id'))
    iso_countryname = Column("iso_countryname",types.VARCHAR(128))
    iso3_nationalcode = Column("iso3_nationalcode",types.VARCHAR(3))
    flickr_countryname = Column("flickr_countryname",types.VARCHAR(128))


    def __init__(self, iso_numcode, continent_id, iso_countryname, iso3_nationalcode, flickr_countryname):
        self.iso_numcode = iso_numcode
        self.continent_id = continent_id
        self.iso_countryname = iso_countryname
        self.iso3_nationalcode = iso3_nationalcode
        self.flickr_countryname = flickr_countryname

class Continent(Base):
    __tablename__ = 'continent'
    id = Column("id", types.Integer, primary_key=True, autoincrement=True)
    name = Column("name",types.VARCHAR(128))

    def __init__(self, name):
        self.name = name
