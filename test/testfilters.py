import shutil
import datetime
import time

from flask.ext.testing import TestCase

from app import db, app
import hactar.filters as filters
import hactar.models

class TestFilters(TestCase):

    whoosh = '/tmp/hactar/whoosh-nosetest'

    def create_app(self):
        import json
        conf = json.load(open('config.json', 'rb'))['test']
        app.config.update(conf)
        hactar.models.setup('test')
        app.logger.setLevel(30)
        app.celery_running = False
        return app

    def setUp(self):
        """Before each test, set up a blank database"""
        try:
            shutil.rmtree(self.whoosh)
        except OSError as err:
            pass
        db.create_all()

    def tearDown(self):
        """Get rid of the database again after each test."""
        db.session.remove()
        db.drop_all()

    def test_datetime(self):
        strf = '%H:%M %d/%m/%Y'
        adate = datetime.datetime(2011, 8, 06, 06, 05)
        filt = filters._jinja2_filter_datetime
        self.assertEqual(adate.strftime(strf), filt(adate))
        now = datetime.datetime.now()
        self.assertEqual(now.strftime(strf), filt(time.time()))
        self.assertEqual(now.strftime(strf), filt(now))

    def test_reldatetime(self):
        strf = '%H:%M %d/%m/%Y'
        now = datetime.datetime(2013, 9, 30, 11, 53)
        date0 = datetime.datetime(2011, 8, 6, 6, 5)
        date1 = datetime.datetime(2012, 8, 6, 6, 5)
        date2 = datetime.datetime(2013, 8, 6, 6, 5)
        date3 = datetime.datetime(2013, 9, 30, 3, 5)
        date4 = datetime.datetime(2013, 9, 30, 11, 40)
        filt = filters._jinja2_filter_reldatetime
        self.assertEqual('2 years ago', filt(date0, now))
        self.assertEqual('13 months ago', filt(date1, now))
        self.assertEqual('55 days ago', filt(date2, now))
        self.assertEqual('9 hours ago', filt(date3, now))
        self.assertEqual('13 minutes ago', filt(date4, now))
        now_really = datetime.datetime.now()
        self.assertEqual('just now', filt(time.time()))
        self.assertEqual('just now', filt(now_really))
        
    def test_status(self):
        stat = filters._jinja2_filter_status 
        self.assertEqual(stat(200), 'OK')
        self.assertEqual(stat(201), 'Created (201)')
        
        self.assertEqual(stat(404), 'Not Found (404)')
        self.assertEqual(stat(500), 'Internal Server Error (500)')
