""" Fabfile for hactar project."""
import os
import json
import re

import cuisine
from fabric.api import cd, env

CONF = json.load(open('config.json', 'rb'))['production']
env.roledefs = {'production': ['vagrant@grumman'],
                'staging': ['vagrant@roger'],
                }

def parent(location):
    """Return the parent directory of a location (i.e. strip last element of
    location name)."""
    if location.startswith(os.path.sep):
        start = os.path.sep
    else:
        start = ''
    parts = location.split(os.path.sep)[:-1]
    return start+os.path.join(*parts)

def passed(output):
    """ Check that the output contains evidence of tests passing."""
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
    if tests-skipped < CONF['MIN_TESTS']:
        return False
    return True

def pull_hactar():
    """A quick method to pull hactar from origin/master"""
    with cd(CONF['ROOT']):
        cuisine.run('git pull')

def send_hactar():
    """Run tests and send local copy to github"""
    cuisine.mode_local()
    cuisine.run('git checkout master')
    test_out = cuisine.run('nosetests')
    if not passed(test_out):
        print test_out
        exit(1)
    cuisine.run('git push')
    cuisine.mode_remote()

def ensure_repo():
    """Setup the hactar repo including parent directories, permissions etc."""
    if not cuisine.dir_exists(os.path.join(CONF['ROOT'], '.git')):
        cuisine.dir_ensure(parent(CONF['ROOT']), mode='774',
                owner=CONF['USER'], group=CONF['USER'])
        cuisine.run('git clone %s %s' % (CONF['GIT'], CONF['ROOT']))
        return True
    else:
        return False

def run_hactar():
    """Restart the tornado service running hactar."""
    cuisine.mode_sudo()
    cuisine.run('/etc/init.d/redis-server restart')
    cuisine.run('/etc/init.d/celeryd restart')
    cuisine.upstart_ensure('hactar')


def release():
    """Get the latest release of hactar (assumes local host will push to github
    master and remote host will pull from it)"""
    send_hactar()
    if not ensure_repo():
        with cd(CONF['ROOT']):
            pull_output = cuisine.run('git pull')
            if 'requirements.txt' in pull_output:
                print '***** requirements modified *****'
            cuisine.run('git clean -f')
    run_hactar()
