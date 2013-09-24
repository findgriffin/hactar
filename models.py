""" models.py 
Database models (using SQLAlchemy) for the hactar application.
"""
from hashlib import sha1
import time
import re
import datetime

from flask.ext.sqlalchemy import SQLAlchemy
import flask.ext.whooshalchemy
import requests

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

class Nugget(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    uri = db.Column(db.String())
    title = db.Column(db.String())
    text = db.Column(db.String())
    added = db.Column(db.DateTime())
    modified = db.Column(db.DateTime())
    checked = db.Column(db.DateTime())
    status_code = db.Column(db.Integer())
    content = db.Column(db.Text(), default='')
    _hash = None
    __searchable__ = ['uri', 'text', 'title']

    def __init__(self, text, uri=None, plugins=None):
#       self.plugins = Plugins() if plugins is None else Plugins(plugins)
        if uri:
            validate_uri(uri)
            self.uri = uri
        if len(text.split()) < 2:
            raise ValueError('Description must be more than one word.')

        self.text = text
        self.added = datetime.datetime.now()
        self.modified = self.added
        self.id = self.getid()
        self.check()

    @property
    def sha1(self):
        """ Return the sha1 hash of this nugget. Use the URL if it exists or
        the description if this nugget has no URI."""
        if self._hash is None:
            if self.uri is not None:
                sha = sha1(self.uri)
            else:
                sha = sha1(self.text)
            self._hash = sha.hexdigest()
        return self._hash

    def getid(self):
        """ Return the (first 15 digits) sha1 hash of this nugget as an
        integer."""
        return int(self.sha1[:15], 16)


    def check(self):
        if self.uri:
            resp = requests.get(self.uri)
            self.status_code = resp.status_code
            title = re.search('<title>(.*)</title>', resp.content)# just title for now
            if title:
                self.title = title.group()
            else:
                self.title = 'unknown'

    def update(self):
        self.check()
        self.modified = datetime.datetime.now()

    def __str__(self):
        return 'nugget: %s|%s|%s|%s' % (self.text, self.uri, 
                self.added, self.modified)

    def __repr__(self):
        return '<Nugget %s>' % self.uri if self.uri else self.id

def validate_uri(uri):
    """ Check that the given URI is valid. Raise an exception if it is not."""
    parts = uri.split(':')
    if len(parts) < 2:
        raise ValueError('URI:%s does not specify a scheme.' % uri)
    elif parts[0] not in URI_SCHEMES and parts[0] != 'urn':
        raise ValueError('URI:%s is not a recognised scheme.' % parts[0])

class Task(db.Model):
    """ A task, something that the user needs to do."""
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String())
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
