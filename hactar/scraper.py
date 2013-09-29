import re
import json
import datetime
import time

from requests import get
import BeautifulSoup as bs
from flask import Flask, current_app
from celery import Celery

from models import Meme, setup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time

conf = json.load(open('config.json', 'rb'))['develop']

celery = Celery("scraper", broker=conf['BROKER_URL'])
celery.conf.update(conf)

def visible(element):
    """Check if a BeautifulSoup element is visible (True) or not (False)"""
    if element.parent.name in ['style', 'script', '[document]', 'head',
            'title']:
        return False
    elif re.match('<!--.*-->', unicode(element)):
        return False
    if len(element) < 1 or element.isspace():
        return False
    return True

def get_uri(meme_id, sesh):
    """ Map meme_id to uri (or None), must be given a db session"""
    memes = sesh.query(Meme).filter(Meme.id == int(meme_id)).all()
    if not memes:
        raise ValueError('meme: %s not found' % meme_id)
    if memes[0].uri:
        return memes[0].uri
    else:
        return None

def get_data(uri):
    """Get the status code, content and title of a html page."""
    resp = get(uri)
    status_code = resp.status_code
    title = re.search('<title>(.*)</title>', resp.content)# just title for now
    texts = bs.BeautifulSoup(unicode(resp.content, errors='ignore')).findAll(text=True)
    page_text = filter(visible, texts)
    if title:
        title = title.group().lstrip('<title>').rstrip('</title>')
    else:
        title = 'unknown'
    return status_code, title, u' '.join(page_text)

@celery.task(name='crawl')
def crawl(meme_id):
    db = create_engine(conf['SQLALCHEMY_DATABASE_URI'])
    Session = sessionmaker(bind=db)
    sesh = Session()
    index_service = setup('develop', session=sesh)


    start = time.time()
    if type(meme_id) == int:
        uri = get_uri(meme_id, sesh)
        if not uri:
            return None
    elif type(meme_id) in (str, unicode):
        uri = meme_id
    status, title, data = get_data(uri)
    timeout = conf["BROKER_TRANSPORT_OPTIONS"]["visibility_timeout"]
    while time.time() < start+timeout:
        now = datetime.datetime.now()
        ngt = sesh.query(Meme).filter(Meme.uri == uri).update({'checked': now, 'status_code': status, 'content': data,
        'title': title})
        print 'session: %s' % dir(sesh)
        if ngt:
            break
        time.sleep(1)
    index_service.before_commit(sesh)
    sesh.commit()
    index_service.after_commit(sesh)
    sesh.close()
    return status, title, data

if __name__ == "__main__":
    import sys
    code, title, text = get_data(sys.argv[-1])
    print "%s: %s" % (title, code)
    print 'text:'
    print text
