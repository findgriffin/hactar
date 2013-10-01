#echo 'starting bootstrap script'
#iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080
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

apt-get install -y git python-pip redis-server

su vagrant -c "git clone /vagrant/ /home/vagrant/hactar"

$LOG_DIR

cd /home/vagrant/hactar
pip install -r requirements.txt
cp etc/hactar.conf /etc/init/hactar.conf
cp etc/celeryd /etc/default/celeryd
$SECRET_DEST=/home/vagrant/secrets.json
cp /vagrant/secrets.json $SECRET_DEST
chmod 400 $SECRET_DEST
chown vagrant.vagrant $SECRET_DEST
mkdir $LOGDIR
chown vagrant.vagrant $LOGDIR

# do database stuff here

# start everything up
/etc/init.d/redis-server restart
/etc/init.d/celeryd start
service hactar start

