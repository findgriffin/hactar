""" Fabfile for hactar project."""
import os
import re

import cuisine
from fabric.api import cd, env

env.hosts = ['auroraborealis.com.au']
LOCATION = 'hactar'
GIT = 'https://github.com/findgriffin/hactar.git'
MIN_TESTS = 13
MAX_SKIP = 5

def passed(output):
    ran = re.findall('Ran \d+ tests', output)
    assert len(ran) == 1
    tests = int(ran[0].split()[1])
    skip = re.findall('OK \(SKIP=\d+\)', output)
    assert len(skip) <= 1
    if skip:
        skipped = int(skip[0].split('=')[-1].rstrip(')'))
    else:
        if not output.endswith('OK'):
            return False
        skipped = 0
    if skipped > MAX_SKIP or tests < MIN_TESTS:
        return False
    return True


def setup_host():
    """ Setup a host to the point where it can run hactar."""
    cuisine.package_ensure('git')
    cuisine.package_ensure('python-pip')
    if not cuisine.dir_exists(os.path.join([LOCATION, '.git'])):
        cuisine.run('git clone %s  %s' % (GIT, LOCATION))
        cuisine.dir_ensure(LOCATION)

def update_deps():
    with cd(LOCATION):
        cuisine.mode_sudo()
        cuisine.python_package_ensure_pip(r='requirements.txt')

def update_hactar():
    """Get the latest release of hactar (assumes git pull will get
    origin/master)"""
    with cd(LOCATION):
        cuisine.run('git pull')
        cuisine.run('git clean')
        if passed(cuisine.run('nosetests')):
            # complete rollout
            pass
        else:
            pass
            # abort





