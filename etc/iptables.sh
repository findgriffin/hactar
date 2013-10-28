#! /bin/sh
# These iptables rules only apply to grumman so they are in a seperate file for
# now
iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080
iptables -A INPUT -i eth0 -p tcp -m limit --limit 25/minute --limit-burst 100
-m multiport --dports 22,80,8080,2222 -m state --state NEW,ESTABLISHED -j ACCEPT
iptables -A OUTPUT -o eth0 -p tcp -m multiport --sports 22,80,8080,2222  -m state --state NEW,ESTABLISHED -j ACCEPT

iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

iptables -A INPUT -p icmp --icmp-type echo-reply -j ACCEPT
iptables -A OUTPUT -p icmp --icmp-type echo-request -j ACCEPT

#iptables -P OUTPUT DROP
iptables -P INPUT DROP
iptables -P FORWARD DROP
