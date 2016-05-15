#!/usr/bin/env bash

set -e

ctx logger info "DNS name server ${dns_ip}"
echo -e "nameserver ${dns_ip}" | sudo tee -a /etc/dnsmasq.resolv.conf
echo 'RESOLV_CONF=/etc/dnsmasq.resolv.conf' | sudo tee -a /etc/default/dnsmasq
sudo service dnsmasq restart
