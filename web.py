# -*- coding: utf-8 -*-
"""
    Hactar Web Interface 
    ~~~~~~
    Using flask framework, based on flaskr example app by Armin Ronacher
    :license: BSD, see LICENSE for more details.
"""
import datetime
from sqlite3 import IntegrityError
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from flask.ext.sqlalchemy import SQLAlchemy


# create our little application :)
app = Flask(__name__)
db = SQLAlchemy(app)

# Load default config and override config from an environment variable
app.config.update(dict(
    SQLALCHEMY_DATABASE_URI='sqlite:////tmp/hactar.db',
    DEBUG=True,
    SECRET_KEY='cricket is a stupid sport',
    USERNAME='admin',
    PASSWORD='cricket'
))
app.config.from_envvar('HACTAR_SETTINGS', silent=True)

###############################################################################
# All this should be moved to models/ or hactar when I can figure out db issue
###############################################################################
from hashlib import sha1
import time
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
class Nugget(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    uri = db.Column(db.String())
    text = db.Column(db.String())
    added = db.Column(db.Integer())
    modified = db.Column(db.Integer())
    keywords = db.Column(db.String())

    def __init__(self, text, uri=None, plugins=None):
#       self.plugins = Plugins() if plugins is None else Plugins(plugins)
        if uri is not None:
            validate_uri(uri)
            self.uri = uri
        if len(text.split()) < 2:
            raise ValueError('Description must be more than one word.')
        self.keywords = ''

        self.text = text
        self.added = int(time.time())
        self.modified = self.added

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

#   @property
#   def id(self):
#       """ Return the (first 15 digits) sha1 hash of this nugget as an
#       integer."""
#       return int(self.sha1[:15], 16)

    
    def create(self):
        for word in self.text.split():
            cleaned = word.lower().strip("""~`!$%^&*(){}[];':",.?""")
            app.logger.debug('adding %s to keywords' % cleaned)
            self.keywords.add(cleaned)
#       self.plugins.run(self, 'create')

    def update(self):
        pass

    def __str__(self):
        return 'nugget: %s|%s|%s|%s|%s' % (self.text, self.uri, self.keywords,
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

###############################################################################

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_nuggets():
    nuggets = Nugget.query.all() # can filter or pageinate
    return render_template('show_nuggets.html', nuggets=nuggets)


@app.route('/add', methods=['POST'])
def add_nugget():
    if not session.get('logged_in'):
        abort(401)
    uri = request.form['uri']
    text = request.form['desc']
    try:
        ngt = Nugget(text=text, uri=uri)
#       ngt.create()
        db.session.add(ngt)
        db.session.commit()
        flash('New nugget was successfully added')
    except ValueError as err:
        flash(err.message)
    except IntegrityError as err:
        if 'primary key must be unique' in err.message.lower():
            flash('Nugget with that URI or description already exists')
    return redirect(url_for('show_nuggets'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_nuggets'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_nuggets'))

@app.template_filter('datetime')
def _jinja2_filter_datetime(date, fmt=None):
    dtime = datetime.datetime.fromtimestamp(date)
    if not fmt:
        fmt = '%H:%M %d/%m/%Y'
    return dtime.strftime(fmt)



if __name__ == '__main__':
    try:
        open(app.config['SQLALCHEMY_DATABASE_URI'], 'rb')
    except IOError:
        db.create_all()
    app.run()
