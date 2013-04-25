from sqlalchemy import (
    Table,
    ForeignKey,
    Column,
    Integer,
    Text,
    types,
    UniqueConstraint,
    Unicode
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.dialects import postgresql

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relation,
    exc
    )

from zope.sqlalchemy import ZopeTransactionExtension

from poab.helpers import timetools

import hashlib
from poab.helpers.pbkdf2.pbkdf2 import pbkdf2_bin
from os import urandom
from base64 import b64encode, b64decode
from itertools import izip


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


SALT_LENGTH = 12
KEY_LENGTH = 24
HASH_FUNCTION = 'sha256'  # Must be in hashlib.
# Linear to the hashing time. Adjust to be high but take a reasonable
# amount of time on your server. Measure with:
# python -m timeit -s 'import passwords as p' 'p.make_hash("something")'
COST_FACTOR = 10000

#n-n-link between log and image tables
log_image_table = Table('log_image', Base.metadata,
    Column('log_id', Integer, ForeignKey('log.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column('image_id', Integer, ForeignKey('image.id',onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint('log_id', 'image_id', name='log_id_image_id'))


log_track_table = Table('log_track', Base.metadata,
    Column('log_id', Integer, ForeignKey('log.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column('track_id', Integer, ForeignKey('track.id',onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint('log_id', 'track_id', name='log_id_track_id'))


author_group_table = Table('author_group', Base.metadata,
    Column('author_id', Integer, ForeignKey('author.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column('group_id', Integer, ForeignKey('group.id',onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint('author_id', 'group_id', name='author_id_group_id'))



class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True)
    name = Column("name", types.UnicodeText, unique=True)
    password = Column(Unicode(80), nullable=False)
    uuid = Column("uuid", postgresql.UUID)
    group = relation('Group', secondary=author_group_table, backref='memberships')

    @property
    def __acl__(self):
        return [
            (Allow, self.name, 'edit'),
        ]

    def __init__(self, name, password, uuid):
        self.name = name
        self._make_hash(password)
        self.uuid = uuid

    def _make_hash(self, password):
        """Generate a random salt and return a new hash for the password."""
        if isinstance(password, unicode):
            password = password.encode('utf-8')
        salt = b64encode(urandom(SALT_LENGTH))
        hashed_password =  'PBKDF2$%s$%i$%s$%s' % (
            HASH_FUNCTION,
            COST_FACTOR,
            salt,
            b64encode(pbkdf2_bin(password, salt, COST_FACTOR, KEY_LENGTH,
                                 getattr(hashlib, HASH_FUNCTION))))
        self.password = hashed_password

    def validate_password(self, password):
        """Check a password against an existing hash."""
        if isinstance(password, unicode):
            password = password.encode('utf-8')
        print password
        algorithm, hash_function, cost_factor, salt, hash_a = self.password.split('$')
        assert algorithm == 'PBKDF2'
        hash_a = b64decode(hash_a)
        hash_b = pbkdf2_bin(password, salt, int(cost_factor), len(hash_a),
                            getattr(hashlib, hash_function))
        assert len(hash_a) == len(hash_b)  # we requested this from pbkdf2_bin()
        # Same as "return hash_a == hash_b" but takes a constant time.
        # See http://carlos.bueno.org/2011/10/timing.html
        diff = 0
        for char_a, char_b in izip(hash_a, hash_b):
            diff |= ord(char_a) ^ ord(char_b)
        return diff == 0


    def _set_password(self, password):
        hashed_password = password

        if isinstance(password, unicode):
            password_8bit = password.encode('UTF-8')
        else:
            password_8bit = password

        salt = sha1()
        salt.update(os.urandom(60))
        hash = sha1()
        hash.update(password_8bit + salt.hexdigest())
        hashed_password = salt.hexdigest() + hash.hexdigest()

        if not isinstance(hashed_password, unicode):
            hashed_password = hashed_password.decode('UTF-8')

        self.password = hashed_password

    @classmethod
    def get_author(self, name):
        try:
            author = DBSession.query(Author).filter(Author.name == name).one()
            return author
        except Exception, e:
            print "Error retrieving author %s: ",e
            return None

    @classmethod
    def get_author_by_id(self, id):
        author = DBSession.query(Author).filter(Author.id == id).one()
        return author

class Group(Base):
    __tablename__ = 'group'
    id = Column(Integer, primary_key=True)
    name = Column("name", types.UnicodeText, unique=True)
    authors = relation('Author', secondary=author_group_table, backref='members')

    def __init__(self, name):
        self.name = name

    @classmethod
    def get_group(self, name):
        group = DBSession.query(Group).filter(Group.name == name).one()
        return group



class Log(Base):
    __tablename__ = 'log'
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    infomarker_id = Column("infomarker_id", types.Integer, ForeignKey('trackpoint.id'))
    topic = Column("topic", types.UnicodeText)
    content = Column("content", types.UnicodeText)
    author = Column(Integer, ForeignKey('author.id',onupdate="CASCADE", ondelete="CASCADE"))
    created = Column("created", types.TIMESTAMP(timezone=False),default=timetools.now())
    uuid = Column("uuid", postgresql.UUID)
    image = relation('Image', secondary=log_image_table, backref='imageref')

    def __init__(self, infomarker_id, topic, content, author, created, uuid):
        self.infomarker_id = infomarker_id
        self.topic = topic
        self.content = content
        self.author = author
        self.created = created
        self.uuid = uuid

    @classmethod
    def get_log_by_uuid(self, uuid):
        try:
            log = DBSession.query(Log).filter(Log.uuid == uuid).one()
            return log
        except Exception, e:
            print "Error retrieving log %s: ",e
            return None

class Track(Base):
    __tablename__ = 'track'
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    date = Column("date", types.TIMESTAMP(timezone=False))
    #author = Column(Integer, ForeignKey('author.id',onupdate="CASCADE", ondelete="CASCADE"))
    distance = Column("distance", types.Numeric(11,4))
    timespan = Column("timespan", types.Interval)
    color = Column("color", types.CHAR(6), default='FF0000')
    uuid = Column("uuid", types.UnicodeText)
    log = relation('Log', secondary=log_track_table, backref='tracklogref')
    #__table_args__ = (
    #    UniqueConstraint('location', 'name', name='track_location_name'),
    #    {}
    #    )
    #TODO: Foreign Key to Etappe/Log?

    def __init__(self, date, author, distance, timespan, color, uuid):
        self.date = date
        self.author = author
        self.distance = distance
        self.timespan = timespan
        self.color = color
        self.uuid = uuid

    @classmethod
    def get_track_by_uuid(self, uuid):
        try:
            track = DBSession.query(Track).filter(Track.uuid == uuid).one()
            return track
        except exc.NoResultFound,e:
            print e
            return None



class Image(Base):
    __tablename__ = 'image'
    id = Column(Integer, primary_key=True)
    name = Column("name", types.UnicodeText)
    location = Column("location", types.UnicodeText)
    title = Column("title", types.UnicodeText)
    comment = Column("comment", types.UnicodeText)
    alt = Column("alt", types.UnicodeText)
    hash = Column("hash", types.UnicodeText)
    hash_990 = Column("hash_990", types.UnicodeText) #hash of the image with 990px width
    author = Column(Integer, ForeignKey('author.id',onupdate="CASCADE", ondelete="CASCADE"))
    last_change = Column(types.TIMESTAMP(timezone=False),default=timetools.now())
    published = Column(types.TIMESTAMP(timezone=False))
    uuid = Column("uuid", postgresql.UUID)
    log = relation('Log', secondary=log_image_table, backref='imagelogref')
    __table_args__ = (
        UniqueConstraint('location', 'name', name='image_location_name'),
        {}
        )

    def __init__(self, name, location, title, comment, alt, hash, hash_990, author, uuid, last_change=timetools.now(), published=None):
        self.name = name
        self.location = location
        self.title = title
        self.alt = alt
        self.comment = comment
        self.hash = hash
        self.hash_990 = hash_990
        self.author = author
        self.uuid = uuid
        self.last_change = last_change
        self.published = published

    def reprJSON(self):
        if self.published:
            published = self.published.strftime("%Y-%m-%d")
        else:
            published = self.published
        return dict(id=self.id, name=self.name, location=self.location, title=self.title,
                    alt=self.alt, comment=self.comment, hash=self.hash, hash_990=self.hash_990, author=self.author,
                    last_change=self.last_change.strftime("%Y-%m-%d"), published=published, uuid=self.uuid)

    @classmethod
    def get_images(self):
        images = DBSession.query(Image).all()
        return images

    @classmethod
    def get_image_by_id(self, id):
        try:
            image = DBSession.query(Image).filter(Image.id == id).one()
            return image
        except Exception, e:
            print "Error retrieving extension %s: ",e
            return None

    @classmethod
    def get_image_by_uuid(self, uuid):
        try:
            image = DBSession.query(Image).filter(Image.uuid == uuid).one()
            return image
        except exc.NoResultFound,e:
            print e
            return None


    @classmethod
    def get_image_by_hash(self, hash):
        try:
            image = DBSession.query(Image).filter(Image.hash == hash).one()
            return image
        except exc.NoResultFound,e:
            print e
            return None


    @classmethod
    def get_image_by_hash_990(self, hash_990):
        try:
            image = DBSession.query(Image).filter(Image.hash_990 == hash_990).one()
            return image
        except exc.NoResultFound,e:
            print e
            return None


class FlickrCredentials(Base):
    __tablename__ = 'flickrcredentials'
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    api_key = Column("api_key", types.UnicodeText)
    api_secret = Column("api_secret", types.UnicodeText)
    author = Column(Integer, ForeignKey('author.id',onupdate="CASCADE", ondelete="CASCADE"))

    def __init__(self, api_key, api_secret, author):
        self.api_key = api_key
        self.api_secret = api_secret
        self.author = author

    @classmethod
    def get_flickrcredentials_by_author(self, author_id):
        try:
            flickrcredentials = DBSession.query(FlickrCredentials).filter(FlickrCredentials.author == author_id).one()
            return flickrcredentials
        except Exception, e:
            print "Error retrieving flickrcredentials %s: ",e
            return None

    @classmethod
    def get_author_by_api_key(self, api_key):
        try:
            flickrcredentials = DBSession.query(FlickrCredentials).filter(FlickrCredentials.api_key == api_key).one()
            return flickrcredentials
        except Exception, e:
            print "Error retrieving flickrcredentials %s: ",e
            return None




class Imageinfo(Base): #old version with integrated flickrdata
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
        self.infomarker = infomarker
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
