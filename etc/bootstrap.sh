iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP
iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080
iptables -A INPUT -i etho0 -p tcp -m multiport --dports 22, 80 -j ACCEPT
iptables -A OUTPUT -i etho0 -p tcp -m multiport --dports 22, 80 -j ACCEPT
iptables -A INPUT -i lo  -j ACCEPT
iptables -A OUTPUT -i lo -j ACCEPT

iptables -A OUTPUT -p icmp --icmp-type echo-request -j ACCEPT
iptables -A INPUT -p icmp --icmp-type echo-reply -j ACCEPT

apt-get install git python-pip redis-server

git clone /vagrant hactar

cd hactar
pip install -r requirements.txt
cp hactar.conf /etc/init.d/hactar.conf
cp etc/celeryd /etc/default/celeryd

# do database stuff here

# start everything up
/etc/init.d/redis-server start
/etc/init.d/celeryd start
service hactar start

