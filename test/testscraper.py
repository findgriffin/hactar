from hashlib import sha1
import shutil
import re
import logging
import SocketServer
import SimpleHTTPServer
import multiprocessing
import random

from flask.ext.testing import TestCase
from nose.tools import set_trace

from app import db, app
import hactar.models
from hactar import scraper
from base import BaseTest

PORT = random.randint(5, 50)+8000

class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """A little test server that will serve this directory for crawling"""
    def log_message(self, format, *args): 
        """Suppress the logging output"""
        pass

class TestScraper(BaseTest):

    _multiprocess_can_split = False

    @classmethod
    def setUpClass(cls):
        httpd = SocketServer.TCPServer(('', PORT), Handler)
        cls.server = multiprocessing.Process(target=httpd.serve_forever)
        cls.server.start()

    def test_get_data(self):
        """Crawl a page"""
        self.login()
        uri = 'http://localhost:%s/README.md' % PORT
        crawled = scraper.get_data(uri)
        self.assertIn('programmer', crawled['content'])

    def test_crawl(self):
        """Crawl a page through scraper.crawl() (i.e. interact with app)"""
        self.login()
        uri = 'http://localhost:%s/README.md' % PORT
        meme_id = int(sha1(uri).hexdigest()[:15], 16)
        rv = self.client.post('/memes', data=dict( what=uri, why='a b'), 
                follow_redirects=True)
        cookie_jar = self.client.cookie_jar._cookies
        cookie = cookie_jar['localhost.local']['/']['session'].value
        crawled = scraper.crawl(meme_id, uri, {'session': cookie},
                client=self.client)
        self.assertEquals(crawled['post'], {'status_code': 200})
        self.assertEquals(crawled['meme']['status_code'], 200)
        self.assertEquals(crawled['meme']['id'], meme_id)
        self.assertEquals(crawled['meme']['uri'], uri)

    def test_crawl_search(self):
        """Crawl a page, then search for page content"""
        self.login()
        uri = 'http://localhost:%s/README.md' % PORT
        meme_id = int(sha1(uri).hexdigest()[:15], 16)
        rv0 = self.client.post('/memes', data=dict( what=uri, why='arthur dent'), 
                follow_redirects=True)
        cookie_jar = self.client.cookie_jar._cookies
        cookie = cookie_jar['localhost.local']['/']['session'].value
        crawled = scraper.crawl(meme_id, uri, {'session': cookie}, client=self.client)
        self.assertEquals(crawled['post'], {'status_code': 200})
        self.assertEquals(crawled['meme']['status_code'], 200)
        self.assertEquals(crawled['meme']['id'], meme_id)
        self.assertEquals(crawled['meme']['uri'], uri)
        rv1 = self.client.get('/memes?q=programmer', follow_redirects=True)
        self.assertIn('arthur', rv1.data)
        self.assertNotIn('Unbelievable. No memes here so far', rv1.data)

    def test_crawl_not_found(self):
        """Try to crawl some nonexistant servers and pages"""
        self.skipTest('Not implemented yet')

    def test_crawl_html(self):
        """Crawl a page"""
        self.login()
        uri = 'http://localhost:%s/test/files/rfc2910.html' % PORT
        title = u'RFC 2910 - Internet Printing Protocol/1.1: Encoding and Transport'
        crawled = scraper.get_data(uri)
        self.assertEquals(crawled['title'], title)
    @classmethod
    def tearDownClass(cls):
        cls.server.terminate()

if __name__ == "__main__":
    server = ThreadingHTTPServer()
    server.run_forever()
