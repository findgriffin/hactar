# Vagrant uses this script to setup everythin that requires sudo priveliges
# except starting init/upstart jobs
#echo 'starting bootstrap script'
iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080
#iptables -A INPUT -i etho0 -p tcp -m multiport --dports 22,80 -j ACCEPT
#
#echo 'got to second bunch of iptables'
#iptables -A OUTPUT -o etho0 -p tcp -m multiport --sports 22,80 -j ACCEPT
#iptables -A INPUT -i lo -j ACCEPT
#iptables -A OUTPUT -o lo -j ACCEPT
#
#
#iptables -A OUTPUT -p icmp --icmp-type echo-request -j ACCEPT
#iptables -A INPUT -p icmp --icmp-type echo-reply -j ACCEPT
#iptables -P INPUT DROP
#iptables -P FORWARD DROP
#iptables -P OUTPUT DROP

apt-get install -y git python-pip redis-server language-pack-en

#
#
#cd /home/vagrant/hactar
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
