import flickrapi

from poab.models  import (
    DBSession,
    Author,
    FlickrCredentials
    )


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
    result=flickr.upload(filename=str(filename),title=title,description=description,tags=tags)
    return result
    
    
    
    
