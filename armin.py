#!/usr/bin/python
#coding:utf-8

import yaml
import client
import logging

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    with open('test.yaml') as f:
        config = yaml.safe_load(f)
    clients = client.generate_ssh_clients(config['test'])
    #for method in config['methods']:
    for _, host in clients.iteritems():
        logger.info(host.server)
        hostname = 'yyy'
        host.set_hostname(hostname)
        #host.update_system()
        #host.set_gateway_and_dns('eth0', '10.10.196.88', ['10.10.99.43',], 'ricebook.com')
        #host.set_hosts(hostname, mfsmaster='10.10.57.167')
        #host.rm_hosts('localhost6.localdomain6')
