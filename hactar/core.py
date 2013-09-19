""" core.py The core of Hactar, connecting the frontend to the backend."""
from hashlib import sha1
import time
import string
import hactar.sqlite
import logging
import os
import re

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

class Plugins():

    def __init__(self, plugin_dir='plugins'):
        plugins = []
        hooks = {
            'nugget': {'create': [], 'update': [], 'delete': []},
            'task':   {'create': [], 'update': [], 'delete': []},
            'user':   {'create': [], 'update': [], 'delete': []},
                    }
        try:
            candidates = os.listdir(plugin_dir)
            logging.debug('plugin candidates: %s' % ', '.join(candidates))
            for candidate in candidates:
                location = os.path.join(plugin_dir, candidate)
                conf = os.path.join(location, '__init__.py')
                if os.path.isdir(location) and os.path.exists(conf):
                    logging.debug('attempting to import plugin:%s' % candidate)
                    try:
                        plugins.append(__import__(location.replace(os.path.sep,
                            '.'), fromlist=['plugins']))
                    except ImportError as err:
                        logging.error('error loading %s plugin:%s' % (
                            candidate, err.message))
        except OSError as err:
            logging.error('error loading plugins:'+err.message)
        if len(plugins) == 0:
            logging.debug('found no plugins to inspect')
        for plugin in plugins:
            logging.debug('inspecting plugin %s ' % plugin)
            for key1 in hooks.keys():
                for key2 in hooks[key1]:
                    name = key1+'_'+key2
                    if name in dir(plugin):
                        logging.debug('%s found in %s' % (name, plugin))
                        hooks[key1][key2].append(getattr(plugin, name))
                    else:
                        logging.debug('%s not found in %s' % (name, plugin))
        self.nugget = hooks['nugget']
        self.task = hooks['task']
        self.user = hooks['user']

    def run(self, obj, task):
        if isinstance(obj, Nugget):
            function_list = self.nugget[task]
        elif isinstance(obj, Task):
            function_list = self.task[task]
        elif isinstance(obj, User):
            function_list = self.user[task]
        else:
            raise ValueError('%s must be Nugget, Task or User, instead it is: %s' % (obj, type(obj)))
        [func(obj) for func in function_list]

class Nugget():
    """ A nugget of information. Consists of description and optional URI."""
    uri = None
    desc = None
    _hash = None
    added = None
    modified = None
    keywords = None
    
    def __init__(self, desc, uri=None, plugins=None):
        self.plugins = Plugins() if plugins is None else Plugins(plugins)
        if uri is not None:
            validate_uri(uri)
            self.uri = uri
        if len(desc.split()) < 2:
            raise ValueError('Description must be more than one word.')
        self.keywords = set()

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

    @property
    def id(self):
        """ Return the (first 15 digits) sha1 hash of this nugget as an
        integer."""
        return int(self.sha1[:15], 16)

    
    def create(self):
        for word in self.desc.split():
            cleaned = word.lower().strip("""~`!$%^&*(){}[];':",.?""")
            logging.debug('adding %s to keywords' % cleaned)
            self.keywords.add(cleaned)
        self.plugins.run(self, 'create')

    def update(self):
        pass

    def __str__(self):
        return 'nugget: %s|%s|%s|%s|%s' % (self.desc, self.uri, self.keywords,
                self.added, self.modified)


def validate_uri(uri):
    """ Check that the given URI is valid. Raise an exception if it is not."""
    parts = uri.split(':')
    if len(parts) < 2:
        raise ValueError('URI:%s does not specify a scheme.' % uri)
    elif parts[0] not in URI_SCHEMES and parts[0] != 'urn':
        raise ValueError('URI:%s is not a recognised scheme.' % parts[0])

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

    # this is just here to make testing easier (eg. inspecting the last nugget
    # added
    last_nugget = None

    def __init__(self, name, backend=None, nuggets=None, tasks=None,
            plugins=None):
        self.name = name
        self.plugins = Plugins() if plugins is None else Plugins(plugins)
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
        ngt.create()
        self.last_nugget = ngt
        logging.debug('about to add '+str(ngt))
        self.backend.add_nugget(ngt)

    def get_nuggets(self, terms=None):
        """ Return the nuggets of this user, filtered by terms."""
        return self.backend.get_nuggets(terms)

