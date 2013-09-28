""" models.py 
Database models (using SQLAlchemy) for the hactar application.
"""
from hashlib import sha1
import time
import datetime
import json

import markdown
from flask.ext.sqlalchemy import SQLAlchemy
from whooshalchemy import IndexService


URI_SCHEMES = [
    'aaa', 'aaas', 'about', 'acap', 'cap', 'cid', 'crid', 'data', 'dav',
    'dict', 'dns', 'fax', 'file', 'ftp', 'geo', 'go', 'gopher', 'h323', 'http',
    'https', 'iax', 'im', 'imap', 'info', 'ldap', 'mailto', 'mid', 'news',
    'nfs', 'nntp', 'pop', 'rsync', 'pres', 'rtsp', 'sip', 'S-HTTP', 'sips',
    'snmp', 'tag', 'tel', 'telnet', 'tftp', 'urn', 'view-source', 'wais', 'ws',
    'wss', 'xmpp', 'afp', 'aim', 'apt', 'bolo', 'bzr', 'callto', 'coffee',
    'cvs', 'daap', 'dsnp', 'ed2k', 'feed', 'fish', 'gg', 'git', 'gizmoproject',
    'irc', 'ircs', 'itms', 'javascript', 'ldaps', 'magnet', 'mms', 'msnim',
    'postal2', 'secondlife', 'skype', 'spotify', 'ssh', 'svn', 'sftp', 'smb',
    'sms', 'steam', 'webcal', 'winamp', 'wyciwyg', 'xfire', 'ymsgr',
]

db = SQLAlchemy()

class Meme(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    uri = db.Column(db.Text())
    title = db.Column(db.Text(), default=unicode(''))
    text = db.Column(db.Text())
    added = db.Column(db.DateTime())
    modified = db.Column(db.DateTime())
    checked = db.Column(db.DateTime())
    status_code = db.Column(db.Integer(), default=-1)
    content = db.Column(db.Text(), default=unicode(''))
    _hash = None
    __searchable__ = ['uri', 'text', 'content', 'title']

    def __init__(self, text, uri=None, plugins=None):
        if is_uri(uri):
            self.uri = uri
        else:
            self.uri = unicode('')
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
        if self._hash is None:
            if self.uri:
                sha = sha1(self.uri)
            else:
                sha = sha1(self.title)
            self._hash = sha.hexdigest()
        return self._hash

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
        return markdown.markdown(self.text)

    def update(self):
#       self.check()
        self.modified = datetime.datetime.now()

    def __str__(self):
        return 'meme: %s|%s|%s|%s' % (self.text, self.heading, 
                self.added, self.modified)

    def __repr__(self):
        return '<Meme %s>' % self.heading 

def is_uri(uri):
    """ Check that the given URI is valid. Raise an exception if it is not."""
    parts = uri.split(':')
    if len(parts) < 2:
        return False
    elif parts[0] not in URI_SCHEMES and parts[0] != 'urn':
        return False
    return True

class Event(db.Model):
    """ A event, something that the user may do or has done."""
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.Text())
    added = db.Column(db.DateTime())
    modified = db.Column(db.DateTime())
    due = db.Column(db.DateTime())
    start_time = db.Column(db.DateTime())
    finish_time = db.Column(db.DateTime())
    priority = db.Column(db.Integer())
    
    def __init__(self, text, due=None, start_time=None, finish_time=None):
        self.text = text
        if due is not None:
            self.due = int(due)
        if start_time is not None:
            self.start_time = int(start_time)
        if finish_time is not None:
            self.finish_time = int(finish_time)
        self.added = time.time()
        self.modified = self.added

def setup(context):
    conf = json.load(open('config.json', 'rb'))[context]
    index_service = IndexService(conf)
    index_service.register_class(Meme)

