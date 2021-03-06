""" models.py 
Database models (using SQLAlchemy) for the hactar application.
"""
from hashlib import sha1
import time
import datetime
from dateutil.parser import parse
from datetime import datetime as dtime
import json

import markdown
from flask.ext.sqlalchemy import SQLAlchemy
from whooshalchemy import IndexService

import pytz

TIMEZONE = 'America/Los_Angeles'

URI_SCHEMES = [ 'aaa', 'aaas', 'about', 'acap', 'cap', 'cid', 'crid', 'data',
'dav', 'dict', 'dns', 'fax', 'file', 'ftp', 'geo', 'go', 'gopher', 'h323',
'http', 'https', 'iax', 'im', 'imap', 'info', 'ldap', 'mailto', 'mid', 'news',
'nfs', 'nntp', 'pop', 'rsync', 'pres', 'rtsp', 'sip', 'S-HTTP', 'sips', 'snmp',
'tag', 'tel', 'telnet', 'tftp', 'urn', 'view-source', 'wais', 'ws', 'wss',
'xmpp', 'afp', 'aim', 'apt', 'bolo', 'bzr', 'callto', 'coffee', 'cvs', 'daap',
'dsnp', 'ed2k', 'feed', 'fish', 'gg', 'git', 'gizmoproject', 'irc', 'ircs',
'itms', 'javascript', 'ldaps', 'magnet', 'mms', 'msnim', 'postal2',
'secondlife', 'skype', 'spotify', 'ssh', 'svn', 'sftp', 'smb', 'sms', 'steam',
'webcal', 'winamp', 'wyciwyg', 'xfire', 'ymsgr',
]
TLDS = ['ac', 'ad', 'ae', 'aero', 'af', 'ag', 'ai', 'al', 'am', 'an', 'ao',
'aq', 'ar', 'arpa', 'as', 'asia', 'at', 'au', 'aw', 'ax', 'az', 'ba', 'bb',
'bd', 'be', 'bf', 'bg', 'bh', 'bi', 'biz', 'bj', 'bm', 'bn', 'bo', 'br', 'bs',
'bt', 'bv', 'bw', 'by', 'bz', 'ca', 'cat', 'cc', 'cd', 'cf', 'cg', 'ch', 'ci',
'ck', 'cl', 'cm', 'cn', 'co', 'com', 'coop', 'cr', 'cu', 'cv', 'cw', 'cx',
'cy', 'cz', 'de', 'dj', 'dk', 'dm', 'do', 'dz', 'ec', 'edu', 'ee', 'eg', 'er',
'es', 'et', 'eu', 'fi', 'fj', 'fk', 'fm', 'fo', 'fr', 'ga', 'gb', 'gd', 'ge',
'gf', 'gg', 'gh', 'gi', 'gl', 'gm', 'gn', 'gov', 'gp', 'gq', 'gr', 'gs', 'gt',
'gu', 'gw', 'gy', 'hk', 'hm', 'hn', 'hr', 'ht', 'hu', 'id', 'ie', 'il', 'im',
'in', 'info', 'int', 'io', 'iq', 'ir', 'is', 'it', 'je', 'jm', 'jo', 'jobs',
'jp', 'ke', 'kg', 'kh', 'ki', 'km', 'kn', 'kp', 'kr', 'kw', 'ky', 'kz', 'la',
'lb', 'lc', 'li', 'lk', 'lr', 'ls', 'lt', 'lu', 'lv', 'ly', 'ma', 'mc', 'md',
'me', 'mg', 'mh', 'mil', 'mk', 'ml', 'mm', 'mn', 'mo', 'mobi', 'mp', 'mq',
'mr', 'ms', 'mt', 'mu', 'museum', 'mv', 'mw', 'mx', 'my', 'mz', 'na', 'name',
'nc', 'ne', 'net', 'nf', 'ng', 'ni', 'nl', 'no', 'np', 'nr', 'nu', 'nz', 'om',
'org', 'pa', 'pe', 'pf', 'pg', 'ph', 'pk', 'pl', 'pm', 'pn', 'post', 'pr',
'pro', 'ps', 'pt', 'pw', 'py', 'qa', 're', 'ro', 'rs', 'ru', 'rw', 'sa', 'sb',
'sc', 'sd', 'se', 'sg', 'sh', 'si', 'sj', 'sk', 'sl', 'sm', 'sn', 'so', 'sr',
'st', 'su', 'sv', 'sx', 'sy', 'sz', 'tc', 'td', 'tel', 'tf', 'tg', 'th', 'tj',
'tk', 'tl', 'tm', 'tn', 'to', 'tp', 'tr', 'travel', 'tt', 'tv', 'tw', 'tz',
'ua', 'ug', 'uk', 'us', 'uy', 'uz', 'va', 'vc', 've', 'vg', 'vi', 'vn', 'vu',
'wf', 'ws', 'xxx', 'ye', 'yt', 'za', 'zm', 'zw']

db = SQLAlchemy()

class Meme(db.Model):
    """The smallest unit of information"""
    id = db.Column(db.Integer, primary_key=True)
    uri = db.Column(db.UnicodeText())
    title = db.Column(db.UnicodeText())
    text = db.Column(db.UnicodeText())
    added = db.Column(db.DateTime())
    modified = db.Column(db.DateTime())
    checked = db.Column(db.DateTime())
    status_code = db.Column(db.Integer(), default=-1)
    content = db.Column(db.UnicodeText())
    _dict = None
    _sha1 = None
    __searchable__ = ['uri', 'text', 'content', 'title']

    def __init__(self, text, uri):
        self.uri = is_uri(uri)
        if self.uri:
            self.title = None
        else:
            self.title = uri
        if len(text.split()) < 2:
            raise ValueError('Description must be more than one word.')

        self.text = text
        self.added = datetime.datetime.now()
        self.modified = self.added
        self.id = self.getid()

    @property
    def sha1(self):
        """ Return the sha1 hash of this meme. Use the URL if it exists or
        the title if this meme has no URI. (it must have one or the other)"""
        if self._sha1 is None:
            if self.uri:
                sha = sha1(self.uri)
            else:
                sha = sha1(self.title)
            self._sha1 = sha.hexdigest()
        return self._sha1

    def getid(self):
        """ Return the (first 15 digits) sha1 hash of this meme as an
        integer."""
        return int(self.sha1[:15], 16)

    @property
    def heading(self):
        if self.title:
            return self.title
        else:
            return self.uri
    
    @property
    def markup(self):
        html = markdown.markdown(self.text)
        # this will fail for
        new_html = html.replace('<ul>', '<ul class="circle">')
        return new_html
    def __str__(self):
        return 'meme: %s|%s|%s|%s' % (self.text, self.heading, 
                self.added, self.modified)

    def __repr__(self):
        return '<Meme %s>' % self.heading 

    def dictify(self):
        """Return a dictionary representation of this event"""
        if not type(self._dict) == dict:
            self._dict = {}
            for field in self.__mapper__.columns:
                value = unicode(getattr(self, field.name))
                self._dict[field.name] = value
        return self._dict

def is_uri(uri):
    """ Check that the given URI is valid. Raise an exception if it is not."""
    parts = uri.split('/')
    if len(parts) > 1:
        hostname = parts[0].split('.')
        if len(hostname) > 1 and hostname[-1] in TLDS:
            return u'http://'+uri
    parts = uri.split(':')
    if len(parts) < 2:
        return None
    elif parts[0] not in URI_SCHEMES and parts[0] != 'urn':
        return None
    return uri

class Action(db.Model):
    """ A event, something that the user may do or has done."""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.Text())
    added = db.Column(db.DateTime())
    modified = db.Column(db.DateTime())
    due = db.Column(db.DateTime(), nullable=True)
    start_time = db.Column(db.DateTime(), nullable=True)
    finish_time = db.Column(db.DateTime(), nullable=True)
    priority = db.Column(db.Integer(), default=0)
    points = db.Column(db.Integer(), default=0)
    _tz = None
    _dict = None
    __searchable__ = ['text']
    
    def __init__(self, text, due=None, start=None, finish=None,
            priority=None, points=None):
        if not text:
            raise ValueError('Action text must not be blank')
        self.text = text
        if due is not None:
            self.due = due
        if start is not None:
            self.start_time = start
        if finish is not None:
            self.finish_time = finish
        if priority is not None:
            self.priority = int(priority)
        if points is not None:
            self.points = int(points)
        self.added = datetime.datetime.now()
        self.modified = self.added

    @property
    def is_task(self):
        """Check if this event is a task (has a due time)"""
        return self.due is not None

    @property
    def is_event(self):
        """Check if this event is a task (has a due time)"""
        if self.start_time or self.finish_time:
            return True
        else:
            return False
            
    @property
    def completed(self):
        """Return None if there is no finish time."""
        return self.finish_time is not None

    @property
    def duration(self):
        """The time this action took, or None if that cannot be determined."""
        if self.start_time is not None and self.finish_time is not None:
            return self.finish_time - self.start_time
        else:
            return None

    @property
    def latent(self):
        if self.start_time is None:
            if self.is_task and not self.completed:
                return True
            else:
                return False
        elif self.start_time > dtime.now():
            return True
        else:
            return False

    @property
    def ongoing(self):
        """Return true if this event has started but not finished."""
        now = dtime.now()
        if self.latent or self.completed or not self.is_task:
            return False
        else:
            return True

    @property
    def completed(self):
        """Return true if there is a finish time and it is in the past."""
        now = dtime.now()
        if self.finish_time is None:
            return False
        elif self.finish_time < now:
            return True
        else:
            return False

    @property
    def start_date(self):
        if self.start_time is not None:
            return self.start_time.date()
        else:
            return None

    @property
    def finish_date(self):
        if self.finish_time is not None:
            return self.finish_time.date()
        else:
            return None

    @property
    def due_date(self):
        if self.due_time is not None:
            return self.due_time.date()
        else:
            return None

    def dt(self, name, tz):
        unaware = getattr(self, name)
        if not hasattr(unaware, 'tzinfo'):
            raise ValueError('%s is not a datetime it is a %s' % (name,
                type(unaware)))
        aware = unaware.replace(tzinfo=pytz.utc)
        if tz == 'utc':
            return aware
        elif tz == 'local':
            return aware.astimezone(self.tz)

    @property
    def tz(self):
        if self._tz is None:
            self._tz = pytz.timezone(TIMEZONE)
        return self._tz

    def dictify(self):
            """Return a dictionary representation of this event"""
            if not type(self._dict) == dict:
                self._dict = {}
                for field in self.__mapper__.columns:
                    value = unicode(getattr(self, field.name))
                    self._dict[field.name] = value
            return self._dict

def setup(context, session=None):
    """Setup the whooshalchemy index service"""
    conf = json.load(open('config.json', 'rb'))[context]
    index_service = IndexService(conf, session=session)
    index_service.register_class(Meme)
    index_service.register_class(Action)
    return index_service

