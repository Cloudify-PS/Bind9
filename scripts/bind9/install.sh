#!/usr/bin/env bash
set -e
ctx logger info "starting DNS..."

# Install BIND.
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install bind9 --yes
# Update BIND configuration with the specified zone and key.
sudo bash -c "echo '127.0.0.1  $(hostname)' >> /etc/hosts"

named_conf_path=$(ctx download-resource scripts/bind9/resources/named.conf.local)
cat ${named_conf_path} | sudo tee /etc/bind/named.conf.local

openstack_conf_path=$(ctx download-resource scripts/bind9/resources/openstacklocal.local)
cat ${openstack_conf_path} | sudo tee /etc/bind/openstacklocal.local

# zone configuration.
ctx logger info "DNS IP address is ${dns_ip}"
sudo echo ${dns_ip} > /home/ubuntu/dnsfile

db_conf_path=$(ctx download-resource scripts/bind9/resources/db.example.com)
sed -e "s/\${ADDRESS}/$(hostname -I)/g" -e "s/\${DATE}/$(date +%Y%m%d%H)/g" -i ${db_conf_path}
cat ${db_conf_path} | sudo tee /var/lib/bind/db.example.com

sudo chown root:bind /var/lib/bind/db.example.com
