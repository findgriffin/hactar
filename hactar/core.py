""" core.py The core of Hactar, connecting the frontend to the backend."""
import hashlib
import time
import sqlite

BACKEND_DEFAULT = sqlite.Sqlite

class Nugget():
    uri = None
    text = None
    _hash = None
    added = None
    modified = None
    keywords = None
    
    def __init__(self, text, uri=None):
        if uri is not None:
            self.uri = uri
        self.text = text
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

    def add_nugget(self, nugget):
        # plugin hooks go here
        self.backend.add_nugget(nugget)

    def get_nuggets(self):
        return self.backend.get_nuggets()
