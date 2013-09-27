""" Fabfile for hactar project."""
import os
import json
import re

import cuisine
from fabric.api import cd, env

CONF = json.load(open('config.json', 'rb'))['production']
env.hosts = [CONF['HOST']]

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

def setup_upstart():
    """ Start upstart job running hactar."""
    cuisine.mode_sudo()
    source = os.path.join(CONF['ROOT'], 'hactar.conf')
    dest = '/etc/init/hactar.conf'
    cuisine.run('rsync %s %s' % (source, dest))

def setup_repo():
    """Setup the hactar repo including parent directories, permissions etc.
    the repo will be group writeable so there is no need to login as the hactar
    user when updating."""
    cuisine.mode_sudo()
    cuisine.dir_ensure(parent(CONF['ROOT']), mode='774', owner=CONF['USER'],
            group=CONF['USER'])
    # root directory with code
    cuisine.dir_ensure(CONF['ROOT'], mode='774', owner=CONF['USER'],
            group=CONF['USER'])
    if not cuisine.dir_exists(os.path.join(CONF['ROOT'], '.git')):
        cuisine.run('su hactar -c "git clone %s  %s"' % (CONF['GIT'], 
            CONF['ROOT']))
    with cd(CONF['ROOT']):
        cuisine.run('git config core.sharedRepository group')
        cuisine.run('chmod -R g+w .')

def setup_host():
    """ Setup a host to the point where it can run hactar."""
    if not cuisine.user_check(CONF['USER']):
        exit(1)
    cuisine.mode_sudo()
    cuisine.package_ensure('git')
    cuisine.package_ensure('python-pip')
    # logs
    cuisine.dir_ensure(CONF['LOG_DIR'], owner=CONF['USER'],
            group=CONF['USER'])
    cuisine.dir_ensure(CONF['WHOOSH_BASE'], owner=CONF['USER'],
            group=CONF['USER'])
    setup_repo()

    setup_upstart()

def update_deps():
    """Used for when we add a new dependancy to hactar."""
    with cd(CONF['ROOT']):
        cuisine.mode_sudo()
        cuisine.python_package_ensure_pip(r='requirements.txt')

def run_hactar():
    """Restart the tornado service running hactar."""
    cuisine.mode_sudo()
    cuisine.upstart_ensure('hactar')

def pull_hactar():
    """A quick method to pull hactar from origin/master"""
    with cd(CONF['ROOT']):
        cuisine.run('git pull')

def update():
    """Get the latest release of hactar (assumes local host will push to github
    master and remote host will pull from it)"""
    cuisine.mode_local()
    cuisine.run('git checkout master')
    test_out = cuisine.run('nosetests')
    if not passed(test_out):
        print test_out
        exit(1)
    cuisine.run('git push')
    cuisine.mode_remote()
    with cd(CONF['ROOT']):
        pull_output = cuisine.run('git pull')
        if 'requirements.txt' in pull_output:
            update_deps()
        if 'hactar.conf' in pull_output:
            setup_upstart()
        cuisine.run('git clean -f')

def update_run():
    """Update and restart tornado service"""
    update()
    run_hactar()


