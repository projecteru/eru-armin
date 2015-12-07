#!/usr/bin/python
#coding:utf-8

import select
import logging

logger = logging.getLogger(__name__)

INTERFACE_CONFIG = '/etc/sysconfig/network-scripts/ifcfg-%s'
GATEWAY_CONFIG = 'GATEWAY=%s'

class Host(object):

    def __init__(self, server, client):
        self.client = client
        self.server = server

    def _execute(self, cmd):
        logger.debug(cmd)
        chan = self.client.get_transport().open_session()
        chan.settimeout(10800)
        try:
            chan.exec_command(cmd)
            while True:
                if chan.exit_status_ready():
                    break
                rl, wl, xl = select.select([chan], [], [], 0.0)
                if len(rl) > 0:
                    if chan.recv_stderr_ready():
                        print chan.recv_stderr(1024),
                    else:
                        print chan.recv(1024),
        except Exception, e:
            logger.error(e)

        exit_status = chan.recv_exit_status()
        logger.info('%s %d' % (cmd, exit_status))
        return exit_status

    def set_hostname(self, hostname):
        logger.info('set hostname')
        cmd = 'hostnamectl set-hostname %s --static' % hostname
        self._execute(cmd)
        cmd = 'hostname %s' % hostname
        self._execute(cmd)

    def set_hosts(self, hostname, **kwargs):
        logger.info('set hosts')
        old = '-'.join(self.server.split('.'))
        cmd = '''sed -i 's/%s/hostname/g' /etc/hosts''' % old
        new = '\n'.join(['%s %s' % (name, server) for name, server in kwargs.iteritems()])
        cmd = '''sed -i '$ a %s' /etc/hosts''' % new
        self._execute(cmd)

    def rm_hosts(self, *args):
        logger.info('delete host')
        s = ';'.join(['/%s$/d' % name for name in args])
        cmd = '''sed -i '%s' /etc/hosts''' % s
        self._execute(cmd)

    def update_system(self):
        logger.info('update system')
        cmd = 'yum update -y'
        self._execute(cmd)

    def set_gateway_and_dns(self, interface, gateway, dns, domain):
        logger.info('set gateway and dns')
        s = ['nameserver %s' % ip for ip in dns]
        if domain:
            s.append('domain %s' % domain)
        cmd = '''echo -e '%s' > /etc/resolv.conf''' % '\n'.join(s)
        config_file = INTERFACE_CONFIG % interface
        gateway = GATEWAY_CONFIG % gateway
        self._execute(cmd)
        # clean ifcfg resolver and getway config
        # set new gateway
        cmd = '''sed -i '/DNS/d;/DOMAIN/d;/GATEWAY/d;/NETMASK/a %s' %s''' % (gateway, config_file)
        self._execute(cmd)
        cmd = 'service network restart'
        self._execute(cmd)

