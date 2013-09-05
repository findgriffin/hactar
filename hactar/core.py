""" core.py The core of Hactar, connecting the frontend to the backend."""
from hashlib import sha1
import time
import string
import hactar.sqlite

BACKEND_DEFAULT = hactar.sqlite.Sqlite

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

class Nugget():
    """ A nugget of information. Consists of description and optional URI."""
    uri = None
    desc = None
    _hash = None
    added = None
    modified = None
    keywords = set()
    
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
        """ Return the sha1 hash of this nugget. Use the URL if it exists or
        the description if this nugget has no URI."""
        if self._hash is None:
            if self.uri is not None:
                sha = sha1(self.uri)
            else:
                sha = sha1(self.desc)
            self._hash = sha.hexdigest()
        return self._hash
    
    def create_index(self):
        for word in self.desc.split():
            self.keywords.add(word.translate(string.maketrans("",""),
                string.punctuation))


def validate_uri(uri):
    """ Check that the given URI is valid. Raise an exception if it is not."""
    parts = uri.split(':')
    if len(parts) < 2:
        raise ValueError('URI:%s does not specify a scheme' % uri)
    elif parts[0] not in URI_SCHEMES and parts[0] != 'urn':
        raise ValueError('URI:%s is not a recognised scheme' % parts[0])



class Task():
    """ A task, something that the user needs to do."""
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
    """ This class represent a user and is a container for nuggets and tasks."""

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
        """ Add a nugget to this users collection."""
        # plugin hooks go here
        ngt = Nugget(desc, uri)
        ngt.create_index()
        self.backend.add_nugget(ngt)

    def get_nuggets(self):
        """ Return all the nuggets of this user."""
        return self.backend.get_nuggets()
