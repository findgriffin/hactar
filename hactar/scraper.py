import re
import json
import datetime
import time

from requests import get
import BeautifulSoup as bs
from flask import Flask, current_app
from celery import Celery

from models import Meme, db, setup

app = current_app


conf = json.load(open('config.json', 'rb'))['develop']

celery = Celery("scraper", broker=conf['BROKER_URL'])
celery.conf.update(conf)

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head',
            'title']:
        return False
    elif re.match('<!--.*-->', str(element)):
        return False
    if len(element) < 1 or element.isspace():
        return False
    return True

def get_uri(meme_id):
    with app.test_request_context():
        memes = Meme.query.filter(Meme.id == int(meme_id)).all()
        if not memes:
            raise ValueError('meme: %s not found' % meme_id)
        if memes[0].uri:
            return memes[0].uri
        else:
            return None

def get_data(uri):
    resp = get(uri)
    status_code = resp.status_code
    title = re.search('<title>(.*)</title>', resp.content)# just title for now
    texts = bs.BeautifulSoup(resp.content).findAll(text=True)
    page_text = filter(visible, texts)
    if title:
        title = title.group().lstrip('<title>').rstrip('</title>')
    else:
        title = 'unknown'
    return status_code, title, ' '.join(page_text)

@celery.task(name='hactar.scaper.crawl')
def crawl(meme_id):
    start = time.time()
    with app.app_context():
        db.session()
        if type(meme_id) == int:
            uri = get_uri(meme_id)
            if not uri:
                return None
        elif type(meme_id) in (str, unicode):
            uri = meme_id
        code, title, data = get_data(uri)
        try:
            setup('develop')
            timeout = conf["BROKER_TRANSPORT_OPTIONS"]["visibility_timeout"]
            while time.time() < start+timeout:
                ngt = Meme.query.filter(Meme.id == int(meme_id))
                if ngt:
                    break
            now = datetime.datetime.now()
            ngt.update({'checked': now, 'status_code': code, 'content': data,
                'title': title})
            ngt[0].update()
            db.session.commit()
        except ValueError as err:
            db.session.rollback()
            print err.message
    return code, title, data



if __name__ == "__main__":
    import sys
    code, title, text = get_data(sys.argv[-1])
    print "%s: %s" % (title, code)
    print 'text:'
    print text
