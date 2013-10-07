"""This module defines celery tasks used by hactar"""
import re
import json
import datetime
import os

from requests import get, post, ConnectionError
import BeautifulSoup as bs
from celery import Celery
from sqlalchemy import create_engine

from models import Meme, setup

ENV = 'production'
ENV_FILE = '.environment'
HEADERS = {}
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

def scrape_html(content):
    """Scrape the page content and return the title (for now)"""
    soup = bs.BeautifulSoup(content)
    texts = soup.findAll(text=True)
    title = soup.title.string
    page_text = filter(visible, texts)
    content = u' '.join(page_text)
    return content, title


def get_data(uri):
    """Get the status code, content and title of a html page."""
    resp = get(uri)
    data = {}
    data['status_code'] = resp.status_code
    content = unicode(resp.content, errors='ignore')
    if 'html' in resp.headers['content-type']:
        data['content'], data['title'] = scrape_html(content)
    else:
        data['content'] = content
    return data

@celery.task(name='crawl')
def crawl(meme_id, url, cookies, client=None):
    """Get data for meme and add it to search index."""
    try:
        data = get_data(url)
    except (ConnectionError, AttributeError) as err:
        # we must always post with status_code because that's how hactar can
        # tell not to run crawl again
        data = {'status_code': -2}

    HEADERS['Cookie'] = 'session=%s' % cookies['session']
    if client:
        resp = client.post('/api/memes/%s' % meme_id, data=data)
    else:
        post_url = 'http://%s:%s/memes/%s' % (conf['DB_HOST'], conf['PORT'],
                meme_id) 
        resp = post(post_url, headers=HEADERS, data=data)
    data['uri'] = url 
    data['id'] = meme_id
    output = {'meme': data}
    output['post'] = {'status_code': resp.status_code}
    return output
