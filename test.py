#!/usr/bin/python
#coding:utf-8

import logging
from armin.client import generate_ssh_clients
from armin.utils import load_config

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    #logging.basicConfig(level=logging.INFO)
    with open('test.yaml') as f:
        config = load_config(f)
    test_config = config['test']
    clients = generate_ssh_clients(test_config)
    count = 1
    for _, host in clients.iteritems():
        logger.info(host.server)
        print host.server
        for method, params in test_config['methods'].iteritems():
            func = getattr(host, method, None)
            if not func:
                logger.info('method %s not allowed', method)
                continue
            print '*'*40
            print method
            #if method in ['services']:
            #    print func(**params)
            if method == 'set_hostname':
                hostname = params.get('hostname')
                #TODO check
                if params.get('incr', False):
                    hostname = '%s%d' % (hostname, count)
                    count += 1
                print func(hostname)
            if method in ['services', 'optimize', 'set_gateway_and_dns', 'set_hosts', 'add_user', 'update_system', 'security_root']:
                print func(**params)
            if method in ['rm_hosts', 'rm_repo', 'add_repo', 'rm_user', 'rm_sudo', 'add_sudo']:
                print func(*params)

