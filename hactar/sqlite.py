""" A simple sqlite backend for Hactar."""
import sqlite3 as lite
import os
from hactar.backend import Backend

TASK_FIELDS = {
    'id': 'INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL',
    'desc': 'TEXT NOT NULL',
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
    'desc': 'TEXT NOT NULL', 
    'added': 'INTEGER', 
    'modified': 'INTEGER',
    'keywords': 'TEXT',
}

class Sqlite(Backend):
    """ This class is the object model for an Sqlite backend."""

    def __init__(self, location, create=True):
        super(Sqlite, self).__init__(location)
        if not os.path.exists(location):
            if not create:
                raise ValueError('backend %s is nonexistant' % location)
            with lite.connect(location) as conn:
                create = 'CREATE TABLE '
                fields = [' '.join(field) for field in NUGGET_FIELDS.items()]
                executestr = create+'nuggets(%s)' % ', '.join(fields)
                execute_sql(self, conn, executestr)
                fields = [' '.join(field) for field in TASK_FIELDS.items()]
                executestr = create+'tasks(%s)' % ', '.join(fields)
                execute_sql(self, conn, executestr)
        else:
            if create:
                raise ValueError('backend %s already exists' % location)
            check_table(TASK_FIELDS, 'tasks', location)
            check_table(NUGGET_FIELDS, 'nuggets', location)

    def add_nugget(self, ngt):
        """ Attempt to add a Nugget object to the database."""
        with lite.connect(self.loc) as conn:
            fields = NUGGET_FIELDS.keys()
            fields.sort()
            insert = 'INSERT INTO nuggets(%s) VALUES ' % ', '.join(fields)
            vals = [ngt.added, ngt.desc, ngt.sha1, ngt.keywords, ngt.modified,
                    ngt.uri] 
            executestr = insert+'(%s)' % ', '.join(format_values(vals))
            execute_sql(self, conn, executestr)

    def get_nuggets(self, terms=None):
        """ Get nuggets filtered by search terms."""
        # just get all nuggets from db and filter them here because I am lazy
        # and don't know how to do it in sql
        with lite.connect(self.loc) as conn:
            executestr = 'SELECT * FROM nuggets'
            rows = execute_sql(self, conn, executestr).fetchall()
        if terms is None:
            return rows
        matched = []
        for term in terms:
            for row in rows:
                if term in row[3]:
                    matched.append(row)
                    rows.remove(row)
                    
        return matched


def check_table(fields, table, location):
    """ Check that table in database location has and only has the given
    fields."""
    with lite.connect(location) as conn:
        # cid|name|type|notnull|dflt_value|pk
        table_info = conn.execute('PRAGMA table_info(%s)' % table).fetchall()
        invalid = 'database %s is invalid because, %s ' % (location, table)
        if not len(table_info) == len(fields):
            raise ValueError(invalid+'has wrong number of columns')
        for col in table_info:
            if not col[1] in fields:
                errstr = invalid+'column %s should not be in schema' % col[1]
                raise KeyError(errstr)
            info = fields[col[1]]
            if not info.startswith(col[2]):
                raise ValueError(invalid+' %s != %s' % (info.split[0], col[2]))
            if 'NOT NULL' in info and col[3] == 0:
                raise ValueError(invalid+' col %s should allow NULL' % col[1])
            elif 'NOT NULL' not in info and col[3] == 1:
                raise ValueError(invalid+' col %s should be NOT NULL' % col[1])
            if 'PRIMARY KEY' in info and col[5] == 0:
                raise ValueError(invalid+' col %s should be PK' % col[1])
            elif 'PRIMARY KEY' not in info and col[5] == 1:
                raise ValueError(invalid+' col %s should not be PK' % col[1])

def format_values(values):
    """ Format a list of values (python objects) for sql statements"""
    for val in values:
        if type(val) == str:
            yield "'"+val+"'"
        elif type(val) == int:
            yield str(val)
        elif type(val) == float:
            yield str(val)
        elif type(val) == set:
            yield '"'+':'.join(val)+'"'
        elif val == None:
            yield 'NULL'
        else:
            raise TypeError('value: %s is of type %s' % (val, type(val)))

def execute_sql(instance, conn, statement):
    instance.log.warn(statement)
    return conn.execute(statement)


