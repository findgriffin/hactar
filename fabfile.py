""" Fabfile for hactar project."""
import os
import json
import re

import cuisine
from fabric.api import cd, env

conf = json.load(open('config.json', 'rb'))
env.hosts = [conf['HOST']]

def parent(location):
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
    if skipped > conf['MAX_SKIP'] or tests < conf['MIN_TESTS']:
        return False
    return True

def setup_upstart():
    """ Start upstart job running hactar."""
    cuisine.mode_sudo()
    source = os.path.join(conf['ROOT'], 'hactar.conf')
    dest = '/etc/init/hactar.conf'
    cuisine.run('rsync %s %s' % (source, dest))

def setup_repo():
    cuisine.mode_sudo()
    cuisine.dir_ensure(parent(conf['ROOT']), mode='774', owner=conf['USER'], 
            group=conf['USER'])
    # root directory with code
    cuisine.dir_ensure(conf['ROOT'], mode='774', owner=conf['USER'], 
            group=conf['USER'])
    if not cuisine.dir_exists(os.path.join(conf['ROOT'], '.git')):
        cuisine.run('su hactar -c "git clone %s  %s"' % (conf['GIT'], conf['ROOT']))

def setup_host():
    """ Setup a host to the point where it can run hactar."""
    if not cuisine.user_check(conf['USER']):
        exit(1)
    cuisine.mode_sudo()
    cuisine.package_ensure('git')
    cuisine.package_ensure('python-pip')
    # logs
    cuisine.dir_ensure(conf['LOG_DIR'], owner=conf['USER'], 
            group=conf['USER'])
    cuisine.dir_ensure(conf['WHOOSH_BASE'], owner=conf['USER'],
            group=conf['USER'])
    setup_repo()

    setup_upstart()

def update_deps():
    """Used for when we add a new dependancy to hactar."""
    with cd(conf['ROOT']):
        cuisine.mode_sudo()
        cuisine.python_package_ensure_pip(r='requirements.txt')

def run_hactar():
    cuisine.mode_sudo()
    cuisine.upstart_ensure('hactar')

def pull_hactar():
    with cd(conf['ROOT']):
        cuisine.run('git pull')

def update_hactar():
    """Get the latest release of hactar (assumes git pull will get
    origin/master)"""
    cuisine.mode_local()
    test_out = cuisine.run('nosetests')
    if not passed(test_out):
        print test_out
        exit(1)
    cuisine.mode_remote()
    cuisine.mode_sudo()
    with cd(conf['ROOT']):
        pull_output = cuisine.run('git pull')
        if 'requirements.txt' in pull_output:
            update_deps()
        cuisine.run('git clean')
    run_hactar()


