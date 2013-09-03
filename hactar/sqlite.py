import sqlite3 as lite
import os
from hactar.core import Nugget
from hactar.core import Task
from hactar.core import User

TASK_FIELDS = {
    'id': 'INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL',
    'text': 'TEXT NOT NULL',
    'added': 'INTEGER',
    'modified': 'INTEGER',
    'due': 'INTEGER',
    'start': 'INTEGER',
    'finish': 'INTEGER',
    'priority': 'INTEGER',
}
NUGGET_FIELDS = {
    'id': 'CHAR(32) PRIMARY KEY NOT NULL', 
    'uri': 'TEXT', 
    'text': 'TEXT NOT NULL', 
    'added': 'INTEGER', 
    'modified': 'INTEGER',
    'keywords': 'TEXT',
}

class Sqlite():
    loc = None
    def __init__(self, location='test.sqlite'):
        self.loc = location
        if not os.path.exists(location):
            with lite.connect(location) as db:
                create = 'CREATE TABLE '
                fields = [' '.join(field) for field in NUGGET_FIELDS.items()]
                executestr = create+'nuggets(%s)' % ', '.join(fields)
                db.execute(executestr)
                fields = [' '.join(field) for field in TASK_FIELDS.items()]
                executestr = create+'tasks(%s)' % ', '.join(fields)
                db.execute(executestr)
        else:
                check_table(TASK_FIELDS, 'tasks', location)
                check_table(NUGGET_FIELDS, 'nuggets', location)

    def add_nugget(self, ngt):
        """ Attempt to add a Nugget object to the database."""
        with lite.connect(self.loc) as db:
            fields = NUGGET_FIELDS.keys()
            fields.sort()
            insert = 'INSERT INTO nuggets(%s) VALUES ' % ', '.join(fields)
            vals = [ngt.added, ngt.sha1, ngt.keywords, ngt.modified, ngt.text,
                    ngt.uri]
            executestr = insert+'(%s)' % ', '.join(format_values(vals))
            db.execute(executestr)


def check_table(fields, table, location):
        with lite.connect(location) as db:
            # cid|name|type|notnull|dflt_value|pk
            table_info = db.execute('PRAGMA table_info(%s)' % table).fetchall()
            invalid = 'database %s is invalid because, %s ' % (location, table)
            if not len(table_info) == len(fields):
                raise ValueError(invalid+'has wrong number of columns')
            for col in table_info:
                if not col[1] in fields:
                    errstr=invalid+'column %s should not be in schema' % col[1]
                    raise KeyError(errstr)
                info = fields[col[1]]
                if not info.startswith(col[2]):
                    raise ValueError(invalid+' %s != %s' % (info.split[0], col[2]))
                if 'NOT NULL' in info and col[3] == 0:
                    raise ValueError(invalid+' column %s should allow NULL' % col[1])
                elif 'NOT NULL' not in info and col[3] == 1:
                    raise ValueError(invalid+' column %s should be NOT NULL' % col[1])
                if 'PRIMARY KEY' in info and col[5] == 0:
                    raise ValueError(invalid+' column %s should be PK' % col[1])
                elif 'PRIMARY KEY' not in info and col[5] == 1:
                    raise ValueError(invalid+' column %s should not be PK' % col[1])

def format_values(values):
    """ Format a list of values (python objects) for sql statements"""
    for val in values:
        if type(val) == str:
            yield "'"+val+"'"
        elif type(val) == int:
            yield str(val)
        elif type(val) == float:
            yield str(val)
        elif val == None:
            yield 'NULL'
