import re
import json
import datetime
import time
import os

from requests import get
import BeautifulSoup as bs
from flask import Flask, current_app
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Meme, setup

ENV_FILE = '.environment'

def get_env():
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, 'rb') as efile:
            return efile.read()
    else:
        return 'production'
ENV = get_env()

conf = json.load(open('config.json', 'rb'))[ENV]

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
    content = unicode(resp.content, errors='ignore')
    texts = bs.BeautifulSoup(content).findAll(text=True)
    page_text = filter(visible, texts)
    if title:
        title = title.group().lstrip('<title>').rstrip('</title>')
    else:
        title = 'unknown'
    return status_code, title, u' '.join(page_text)

@celery.task(name='crawl')
def crawl(meme_id):
    """Get data for meme and add it to search index."""
    engine = create_engine(conf['SQLALCHEMY_DATABASE_URI'])
    sesh = sessionmaker(bind=engine)()
    index_service = setup(ENV, session=sesh)


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
        upd = {'checked': now, 'status_code': status, 'content': data,
                'title': title}
        ngt = sesh.query(Meme).filter(Meme.uri == uri).update(upd)
        if ngt:
            break
        time.sleep(1)
    index_service.before_commit(sesh)
    sesh.commit()
    index_service.after_commit(sesh)
    sesh.close()
    return status, title, data
