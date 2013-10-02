#! /bin/sh
# Vagrant uses this script to setup everything that requires sudo priveliges
# except iptables rules and starting init/upstart jobs

apt-get install -y git python-pip redis-server language-pack-en

pip install -r /vagrant/requirements.txt
cp /vagrant/etc/hactar.conf /etc/init/hactar.conf
cp /vagrant/etc/celeryd /etc/default/celeryd
cp /vagrant/etc/celeryd-init /etc/init.d/celeryd
chmod +x /etc/init.d/celeryd

LOGDIR="/var/log/hactar"
CELERY_LOG="/var/log/celery"
CELERY_RUN="/var/run/celery"
mkdir $LOGDIR
chown vagrant.vagrant $LOGDIR
mkdir $CELERY_LOG
chown vagrant.vagrant $CELERY_LOG
mkdir $CELERY_RUN
chown vagrant.vagrant $CELERY_RUN
