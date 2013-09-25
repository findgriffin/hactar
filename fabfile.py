""" Fabfile for hactar project."""
import cuisine
import os
from fabric.api import cd, env

env.hosts = ['auroraborealis.com.au']
LOCATION = 'hactar'
GIT = 'https://github.com/findgriffin/hactar.git'

def setup_host():
    """ Setup a host to the point where it can run hactar."""
    cuisine.connect("david@auroraborealis.com.au")
    cuisine.package_ensure('git')
    cuisine.package_ensure('python-pip')
    if not cuisine.dir_exists(os.path.join([LOCATION, '.git'])):
        cuisine.run('git clone %s  %s' % (git, location))
        cuisine.dir_ensure(LOCATION)

def update_hactar():
    """Get the latest release of hactar (assumes git pull will get
    origin/master)"""
    with cd(LOCATION):
        cuisine.run('git pull')
    with cd(LOCATION):
        cuisine.python_package_ensure_pip(r='requirements.txt')



