#! /bin/sh
# These iptables rules only apply to grumman so they are in a seperate file for
# now
iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -A INPUT -i eth0 -p tcp -m multiport --dports 22,80,2222 -j ACCEPT
iptables -A OUTPUT -o eth0 -p tcp -m multiport --sports 22,80,2222 -j ACCEPT

iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT
iptables -A INPUT -p icmp --icmp-type echo-reply -j ACCEPT
iptables -A OUTPUT -p icmp --icmp-type echo-request -j ACCEPT
iptables -A INPUT -i eth0
#iptables -P OUTPUT DROP
