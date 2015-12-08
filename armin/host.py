#!/usr/bin/python
#coding:utf-8

import os
import select
import logging
from armin import config
from armin.user import User, Root
from armin.service import Service
from armin.utils import get_random_passwd

logger = logging.getLogger(__name__)

class Host(object):

    def __init__(self, server, client):
        self.client = client
        self.server = server

    def _add_sudo(self, username):
        cmd = '''gpasswd -a %s wheel''' % username
        code, err = self._execute(cmd)
        if code != config.EXECUTE_OK:
            logger.info(err)
            return False
        return True

    def _set_password(self, username, password):
        cmd = '''echo -e '{password}\n{password}\n' | passwd {username} --stdin'''.format(
            password = password, username = username,
        )
        code, err = self._execute(cmd)
        if code != config.EXECUTE_OK:
            logger.info(err)
            return False
        return True

    def _execute(self, cmd):
        logger.debug(cmd)
        chan = self.client.get_transport().open_session()
        chan.settimeout(10800)
        try:
            chan.exec_command(cmd)
            while True:
                if chan.exit_status_ready():
                    break
                rl, wl, xl = select.select([chan], [], [], 0.1)
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
            return False
        else:
            logger.info('upload %s to %s success', src, dst)
        finally:
            sftp.close()
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
        new = '\n'.join(['%s %s' % (server, name) for name, server in kwargs.iteritems()])
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
            result[repo] = True
            target = os.path.join(config.REMOTE_REPO_DIR, repo)
            cmd = 'rm -rf %s' % target
            code, err = self._execute(cmd)
            if code != config.EXECUTE_OK:
                logger.info(err)
                result[repo] = False
        return result

    def add_user(self, **kwargs):
        result = {}
        for username, params in kwargs.iteritems():
            result[username] = {'add': False}
            user = User(username=username, **params)
            cmd = '''%s -d %s -m -u %d -U -s %s %s''' % (
                config.USERADD_BIN,
                user.get_home(),
                user.uid,
                user.get_shell(),
                user.username,
            )
            code, err = self._execute(cmd)
            if code != config.EXECUTE_OK:
                logger.info(err)
                continue
            result[username]['add'] = True
            password = user.get_password(config.PASSWORD_LENGTH)
            if not self._set_password(username, password):
                continue
            result[username]['password'] = password
            if user.login and user.get_key():
                cmd = '''mkdir -p {ssh_path} && echo {content} > {authorized_keys} && chown -R {username}:{username} {ssh_path} && chmod 600 {authorized_keys}'''.format(
                    ssh_path = user.get_ssh_path(),
                    authorized_keys = user.get_authorized_keys_path(),
                    username = username,
                    content = user.get_key(),
                )
                code, err = self._execute(cmd)
                if code != config.EXECUTE_OK:
                    logger.info(err)
                    continue
                result[username]['key_auth'] = True
            if user.sudo:
                result[username]['sudo'] = self._add_sudo(username)
        return result

    def rm_user(self, *args):
        result = {}
        for username in args:
            result[username] = True
            cmd = '''userdel -r -f %s''' % username
            code, err = self._execute(cmd)
            if code != config.EXECUTE_OK:
                logger.info(err)
                result[username] = False
        return result

    def rm_sudo(self, *args):
        result = {}
        for username in args:
            result[username] = True
            cmd = '''gpasswd -d %s wheel''' % username
            code, err = self._execute(cmd)
            if code != config.EXECUTE_OK:
                logger.info(err)
                result[username] = False
        return result

    def add_sudo(self, *args):
        result = {}
        for username in args:
            result[username] = self._add_sudo(username)
        return result

    def security_root(self, random_password=False, root_key=False, security_login=None):
        result = {'random_password': False, 'root_key': False, 'security_login': False}

        password = get_random_passwd(config.PASSWORD_LENGTH)
        if random_password and self._set_password('root', password):
            result['random_password'] = True

        if security_login:
            cmd = '''sed -i 's/#PermitEmptyPasswords/PermitEmptyPasswords/g;s/#PermitRootLogin yes/PermitRootLogin no/g' {config}'''.format(config=config.SSHD_CONFIG)
            cmd += ''' && sed -i '/Match/d;$d' {config}'''.format(config=config.SSHD_CONFIG)
            cmd += ''' && sed -i '$a Match Address {addr}\\n   PermitRootLogin yes' {config}'''.format(addr=','.join(security_login), config=config.SSHD_CONFIG)
            cmd += ''' && service sshd restart'''
            code, err = self._execute(cmd)
            if code != config.EXECUTE_OK:
                logger.info(err)
            else:
                result['security_login'] = True

        if root_key:
            cmd = '''mkdir -p {root_ssh_path}'''.format(root_ssh_path=Root.get_ssh_path())
            cmd += ''' && echo {content} > {root_authorized_keys}'''.format(
                    content=Root.get_key(),
                    root_authorized_keys=Root.get_authorized_keys_path()
            )
            cmd += ''' && chmod 600 {root_authorized_keys}'''.format(root_authorized_keys=Root.get_authorized_keys_path())
            code, err = self._execute(cmd)
            if code != config.EXECUTE_OK:
                logger.info(err)
            else:
                result['root_key'] = True

        return result

    def optimize(self, ulimit=False, sysctl=False):
        result = {}

        if sysctl and self._upload(config.LOCAL_SYSCTL_FILE, '/tmp/init.py'):
            cmd = 'python /tmp/init.py && rm -rf /tmp/init.py'
            code, err = self._execute(cmd)
            if code != config.EXECUTE_OK:
                logger.info(err)
            else:
                result['sysctl'] = True

        if ulimit:
            result['ulimit'] = self._upload(config.LOCAL_ULIMIT_CONF, config.REMOTE_ULIMIT_CONF)

        return result

    def services(self, install=None, modify=None, restart=None):
        svrs = Service(self)
        result = {}
        if install:
            r = {}
            for service, params in install.iteritems():
                r[service] = False
                name = service.replace('-', '_')
                func = getattr(svrs, 'install_%s' % name, None)
                if func:
                    r[service] = func(**params)
            result['install'] = r

        if modify:
            r = {}
            for service, params in modify.iteritems():
                r[service] = False
                name = service.replace('-', '_')
                func = getattr(svrs, 'modify_%s' % name, None)
                if func:
                    r[service] = func(**params)
            result['modify'] = r

        if restart:
            r = svrs.restart(restart)
            result['restart'] = r

        return result

