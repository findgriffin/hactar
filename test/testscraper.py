import unittest
from hashlib import sha1
import shutil
import re
import logging

from flask.ext.testing import TestCase
from nose.tools import set_trace;

from app import db, app
import hactar.models
from hactar import scraper
from base import BaseTest

class TestScraper(BaseTest):

    def test_crawl(self):
        """Crawl a page"""
        self.login()
        uri = 'http://en.wikipedia.org'
        meme_id = int(sha1(uri).hexdigest()[:15], 16)
        rv = self.client.post('/memes', data=dict( what=uri, why='a b'), 
                follow_redirects=True)
        cookie_jar = self.client.cookie_jar._cookies
        cookie = cookie_jar['localhost.local']['/']['session'].value
        status = scraper.crawl(meme_id, uri, {'session': cookie},
                client=self.client)
        self.assertEqual(status, 200)

    def test_crawl_search(self):
        """Crawl a page, then search for page content"""
        self.login()
        uri = 'http://en.wikipedia.org'
        meme_id = int(sha1(uri).hexdigest()[:15], 16)
        rv0 = self.client.post('/memes', data=dict( what=uri, why='arthur dent'), 
                follow_redirects=True)
        cookie_jar = self.client.cookie_jar._cookies
        cookie = cookie_jar['localhost.local']['/']['session'].value
        status = scraper.crawl(meme_id, uri, {'session': cookie},
                client=self.client)
        logging.debug('crawled: %s' % uri)
        self.assertEqual(status, 200)
        rv1 = self.client.get('/memes?q=encyclopedia', follow_redirects=True)
        self.assertIn('Wikipedia', rv1.data)
        self.assertNotIn('Unbelievable. No memes here so far', rv1.data)

    def test_crawl_not_found(self):
        """Try to crawl some nonexistant servers and pages"""
        self.skipTest('Not implemented yet')
