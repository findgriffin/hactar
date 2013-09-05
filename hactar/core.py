""" core.py The core of Hactar, connecting the frontend to the backend."""
import hashlib
import time
import sqlite

BACKEND_DEFAULT = sqlite.Sqlite

URI_SCHEMES=[
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

class Nugget():
    uri = None
    desc = None
    _hash = None
    added = None
    modified = None
    keywords = None
    
    def __init__(self, desc, uri=None):
        if uri is not None:
            validate_uri(uri)
            self.uri = uri
        if len(desc.split()) < 2:
            raise ValueError('description must be more than one word')

        self.desc = desc
        self.added = time.time()
        self.modified = self.added

    @property
    def sha1(self):
        if self._hash is None:
            if self.uri is not None:
                sha = hashlib.sha1(self.uri)
            else:
                sha = hashlib.sha1(self.text)
            self._hash = sha.hexdigest()
        return self._hash

def validate_uri(uri):
    parts = uri.split(':')
    if len(parts) < 2:
        raise ValueError('URI:%s does not specify a scheme' % uri)
    elif parts[0] not in URI_SCHEMES and parts[0] != 'urn':
        raise ValueError('URI:%s is not a recognised scheme' % parts[0])



class Task():
    text = None
    due = None
    start = None
    finish = None
    _hash = None
    added = None
    modified = None
    priority = 0
    
    def __init__(self, text, due=None, start=None, finish=None):
        self.text = text
        if due is not None:
            self.due = int(due)
        if start is not None:
            self.start = int(start)
        if finish is not None:
            self.finish = int(finish)
        self.added = time.time()
        self.modified = self.added

class User():

    nuggets = {}
    tasks = {}
    name = None
    backend = None

    def __init__(self, name, backend=None, nuggets=None, tasks=None):
        self.name = name
        if backend is None or type(backend) == str:
            if type(backend) == str:
                backend_loc = backend+'.sqlite'
            else:
                backend_loc = name+'.sqlite'
            self.backend = BACKEND_DEFAULT(backend_loc, create=False)
        else:
            self.backend = backend
        if nuggets is not None:
            self.nuggets = nuggets
        if tasks is not None:
            self.tasks = tasks

    def add_nugget(self, desc, uri=None):
        # plugin hooks go here
        ngt = Nugget(desc, uri)
        self.backend.add_nugget(ngt)

    def get_nuggets(self):
        return self.backend.get_nuggets()
