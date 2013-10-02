"""This module defines celery tasks used by hactar"""
import re
import json
import datetime
import time
import os

from requests import get, post
import BeautifulSoup as bs
from flask import Flask, current_app
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, OperationalError

from models import Meme, setup

ENV = 'production'
ENV_FILE = '.environment'

if os.path.exists(ENV_FILE):
    with open(ENV_FILE, 'rb') as efile:
        ENV = efile.read()

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
    data = {}
    data['status_code'] = resp.status_code
    content = unicode(resp.content, errors='ignore')
    title = re.search('<title>(.*)</title>', content)# just title for now
    texts = bs.BeautifulSoup(content).findAll(text=True)
    page_text = filter(visible, texts)
    if title:
        data['title'] = title.group().lstrip('<title>').rstrip('</title>')
    data['content'] = u' '.join(page_text)
    return data

@celery.task(name='crawl')
def crawl(meme_id, url, cookies, client=None):
    """Get data for meme and add it to search index."""
    data = get_data(url)
    if client:
        resp = client.post('/memes/%s' % meme_id, data=data)
    else:
        post_url = 'http://%s:%s/memes/%s' % (conf['DB_HOST'], conf['PORT'],
                meme_id) 
        resp = post(post_url, cookies=cookies, data=data)
    if json.loads(resp.data)[str(meme_id)]:
        return data['status_code']
    else: 
        return 'failed to post crawl data'
