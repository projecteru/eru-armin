#!/usr/bin/python
#coding:utf-8

import os
import select
import logging
from armin import config

logger = logging.getLogger(__name__)

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
                    #TODO be nice
                    print chan.recv(1024),
        except Exception, e:
            logger.error(e)
            return config.EXECUTE_EXCEPTION_CODE, str(e)

        exit_status = chan.recv_exit_status()
        logger.info('%s exit code %d' % (cmd, exit_status))
        if exit_status != 0:
            data = chan.recv_stderr(1024)
            err = ''
            while data:
                err += data
                data = chan.recv_stderr(1024)
            return exit_status, err
        else:
            return exit_status, ''

    def _upload(self, src, dst):
        sftp = self.client.get_transport().open_sftp_client()
        try:
            sftp.put(src, dst)
        except Exception, e:
            logger.error(e)
        else:
            logger.info('upload %s to %s success', src, dst)
        finally:
            sftp.close()
            return False
        return True

    def set_hostname(self, hostname):
        logger.info('set hostname')
        cmd = 'hostnamectl set-hostname %s --static' % hostname
        code, err = self._execute(cmd)
        if code != config.EXECUTE_OK:
            logger.info(err)
            return False
        cmd = 'hostname %s' % hostname
        code, err = self._execute(cmd)
        if code != config.EXECUTE_OK:
            logger.info(err)
            return False
        return True

    def set_hosts(self, **kwargs):
        logger.info('set hosts')
        old = '-'.join(self.server.split('.'))
        cmd = '''sed -i 's/%s/'"$HOSTNAME"'/g' %s''' % (old, config.HOSTS_CONF)
        code, err = self._execute(cmd)
        if code != config.EXECUTE_OK:
            logger.info(err)
            return False
        new = '\n'.join(['%s %s' % (name, server) for name, server in kwargs.iteritems()])
        cmd = '''sed -i '$ a %s' %s''' % (new, config.HOSTS_CONF)
        code, err = self._execute(cmd)
        if code != config.EXECUTE_OK:
            logger.info(err)
            return False
        return True

    def rm_hosts(self, *args):
        logger.info('delete host')
        s = ';'.join(['/%s$/d' % name for name in args])
        cmd = '''sed -i '%s' %s''' % (s, config.HOSTS_CONF)
        code, err = self._execute(cmd)
        if code != config.EXECUTE_OK:
            logger.info(err)
            return False
        return True

    def update_system(self, quite=False):
        logger.info('update system')
        cmd = 'yum update -y'
        if quite:
            cmd = 'yum update -y -q'
        code, err = self._execute(cmd)
        if code != config.EXECUTE_OK:
            logger.info(err)
            return False
        return True

    def set_gateway_and_dns(self, interface, gateway, dns, domain):
        logger.info('set gateway and dns')
        s = ['nameserver %s' % ip for ip in dns]
        if domain:
            s.append('domain %s' % domain)
        cmd = '''echo -e '%s' > %s''' % ('\n'.join(s), config.RESOLV_CONF)
        config_file = config.INTERFACE_CONFIG % interface
        gateway = config.GATEWAY_CONFIG % gateway
        code, err = self._execute(cmd)
        if code != config.EXECUTE_OK:
            logger.info(err)
            return False
        # clean ifcfg resolver and getway config
        # set new gateway
        cmd = '''sed -i '/DNS/d;/DOMAIN/d;/GATEWAY/d;/NETMASK/a %s' %s''' % (gateway, config_file)
        code, err = self._execute(cmd)
        if code != config.EXECUTE_OK:
            logger.info(err)
            return False
        cmd = 'systemctl restart network -q'
        code, err = self._execute(cmd)
        if code != config.EXECUTE_OK:
            logger.info(err)
            return False
        return True

    def add_repo(self, *args):
        result = {}
        for repo in args:
            src = os.path.join(config.LOCAL_REPO_DIR, repo)
            dst = os.path.join(config.REMOTE_REPO_DIR, repo)
            result[repo] = self._upload(src, dst)
        return result

    def rm_repo(self, *args):
        result = {}
        for repo in args:
            target = os.path.join(config.REMOTE_REPO_DIR, repo)
            cmd = 'rm -rf %s' % target
            code, err = self._execute(cmd)
            if code != config.EXECUTE_OK:
                logger.info(err)
                result[repo] = False
            else:
                result[repo] = True
        return result

    def add_user(self, **kwargs):
        pass

    def rm_user(self, *args):
        pass

