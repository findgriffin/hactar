import shutil
import datetime
import time

from flask.ext.testing import TestCase
import pytz

from app import db, app
import hactar.filters as filters
import hactar.models

class TestFilters(TestCase):
    _multiprocess_can_split = True

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
        
    def test_future_reldatetime(self):
        strf = '%H:%M %d/%m/%Y'
        now = datetime.datetime(2013, 9, 1, 11, 53)
        date0 = datetime.datetime(2015, 9, 2, 11, 53)
        date1 = datetime.datetime(2014, 10, 6, 6, 5)
        date2 = datetime.datetime(2013, 10, 27, 6, 5)
        date3 = datetime.datetime(2013, 9, 1, 20, 45)
        date4 = datetime.datetime(2013, 9, 1, 12, 6)
        date5 = datetime.datetime(2013, 9, 1, 11, 54)
        date6 = datetime.datetime(2013, 9, 2, 11, 53)
        filt = filters._jinja2_filter_reldatetime
        self.assertEqual('in 2 years', filt(date0, now))
        self.assertEqual('in 13 months', filt(date1, now))
        self.assertEqual('in 55 days', filt(date2, now))
        self.assertEqual('in 9 hours', filt(date3, now))
        self.assertEqual('in 13 minutes', filt(date4, now))
        self.assertEqual('in 60 seconds', filt(date5, now))
        self.assertEqual('tomorrow', filt(date6, now))
        now_really = datetime.datetime.now()
        self.assertEqual('just now', filt(time.time()))
        self.assertEqual('just now', filt(now_really))

    def test_utcreldatetime(self):
        strf = '%H:%M %d/%m/%Y'
        tz = pytz.timezone('America/Los_Angeles')
        now = datetime.datetime(2013, 9, 30, 11, 53, tzinfo=tz)
        now_utc = now.astimezone(pytz.utc)
        now_naive = now_utc.replace(tzinfo=None)
        date2 = datetime.datetime(2013, 8, 6, 6, 5, tzinfo=tz)
        date3 = datetime.datetime(2013, 9, 30, 3, 5, tzinfo=tz)
        date4 = datetime.datetime(2013, 9, 30, 11, 40, tzinfo=tz)
        date4_utc = date4.astimezone(pytz.utc)
        date4_naive = date4_utc.replace(tzinfo=None)
        filt = filters._jinja2_filter_utcreldatetime
        self.assertEqual('55 days ago', filt(date2, now))
        self.assertEqual('9 hours ago', filt(date3, now))
        few_mins = '13 minutes ago'
        self.assertEqual(few_mins, filt(date4, now))
        self.assertEqual(few_mins, filt(date4, now_utc))
        self.assertEqual(few_mins, filt(date4, now_naive))
        self.assertEqual(few_mins, filt(date4_utc, now))
        self.assertEqual(few_mins, filt(date4_utc, now_utc))
        self.assertEqual(few_mins, filt(date4_utc, now_naive))
        self.assertEqual(few_mins, filt(date4_naive, now))
        self.assertEqual(few_mins, filt(date4_naive, now_utc))
        self.assertEqual(few_mins, filt(date4_naive, now_naive))
        now_really = tz.localize(datetime.datetime.now())
        self.assertEqual('just now', filt(now_really))

    def test_reldate(self):
        date = datetime.datetime(2013, 11, 05, 11, 40).date()
        filt = filters._jinja2_filter_reldate
        self.assertEqual(filt(date), 'Tue  5')
        self.assertEqual(filt(date, 'short'), 'Tue')
        self.assertEqual(filt(date, 'long'), 'Tuesday 05/11')

    def test_status(self):
        stat = filters._jinja2_filter_status 
        self.assertEqual(stat(200), 'OK')
        self.assertEqual(stat(201), 'Created (201)')
        
        self.assertEqual(stat(404), 'Not Found (404)')
        self.assertEqual(stat(500), 'Internal Server Error (500)')
