#!/usr/bin/python
#coding:utf-8

import os
import select
import logging
from armin import config
from armin.user import User, Root
from armin.services import get_service
from armin.utils import get_random_passwd

logger = logging.getLogger(__name__)

class Host(object):

    def __init__(self, server, client):
        self.client = client
        self.server = server

    def _add_sudo(self, username):
        cmd = '''gpasswd -a %s wheel''' % username
        return self._execute(cmd)

    def _set_password(self, username, password):
        cmd = '''echo -e '{password}\n{password}\n' | passwd {username} --stdin'''.format(
            password = password, username = username,
        )
        return self._execute(cmd)

    def _execute(self, cmd):
        #logger.debug(cmd)
        #TODO be nice
        chan = self.client \
            .get_transport() \
            .open_session( \
                window_size=2147483647, \
                max_packet_size=2147483647, \
            )
        chan.setblocking(0)
        try:
            chan.exec_command(cmd)
            while True:
                data = False
                rl, wl, xl = select.select([chan], [], [], 1)
                if chan in rl and chan.recv_stderr_ready():
                    print chan.recv_stderr(1024),
                    data = True
                elif chan in rl and chan.recv_ready():
                    print chan.recv(1024),
                    data = True
                if not data \
                    and (chan.exit_status_ready() or chan.closed) \
                    and not chan.recv_stderr_ready() \
                    and not chan.recv_ready():
                    chan.shutdown(2)
                    break
        except Exception, e:
            logger.exception(e)
            return False

        exit_status = chan.recv_exit_status()
        print cmd, exit_status
        return exit_status == config.EXECUTE_OK

    def _upload(self, src, dst):
        sftp = self.client.get_transport().open_sftp_client()
        try:
            sftp.put(src, dst)
        except Exception, e:
            logger.exception(e)
            return False
        else:
            logger.info('upload %s to %s success', src, dst)
        finally:
            sftp.close()
        return True

    def _replace_hosts(self, old, new):
        cmd = '''sed -i '/^%s/{h;s/.*/%s/};${x;/^$/{s//%s/;H};x}' %s '''
        cmd = cmd % (old, new, new, config.HOSTS_CONF)
        return self._execute(cmd)

    def run_commands(self, *args):
        return dict([
            (command, self._execute(command)) for command in args
        ])

    def set_hostname(self, hostname):
        logger.info('set hostname')
        cmd = 'hostnamectl set-hostname %s --static' % hostname
        cmd += ' && hostname %s' % hostname
        if not self._execute(cmd):
            return False

        old = "%s '$HOSTNAME'" % self.server
        new = "%s %s" % (self.server, hostname)
        local_new = "127.0.0.1 %s" % hostname
        return self._replace_hosts(old, new) and self._replace_hosts("127.0.0.1 '$HOSTNAME'", local_new)

    def set_hosts(self, **kwargs):
        logger.info('set hosts')
        result = dict([
            (server, self._replace_hosts(server, '%s %s' % (server, name))) for server, name in kwargs.iteritems()
        ])
        return result

    def rm_hosts(self, *args):
        logger.info('delete host')
        s = ';'.join(['/%s$/d' % name for name in args])
        cmd = '''sed -i '%s' %s''' % (s, config.HOSTS_CONF)
        return self._execute(cmd)

    def update_system(self, quite=False):
        logger.info('update system')
        cmd = 'yum update -y'
        if quite:
            cmd = 'yum update -y -q'
        return self._execute(cmd)

    def set_gateway(self, interface, gateway):
        logger.info('set gateway')
        config_file = config.INTERFACE_CONFIG % interface
        # clean ifcfg resolver and getway config
        # set new gateway
        gateway = config.GATEWAY_CONFIG % gateway
        cmd = '''sed -i '/DNS/d;/DOMAIN/d;/GATEWAY/d;/NETMASK/a %s' %s && systemctl restart network -q''' % (gateway, config_file)
        return self._execute(cmd)

    def set_dns(self, dns, domain=None):
        logger.info('set dns')
        s = ['nameserver %s' % ip for ip in dns]
        if domain:
            s.append('domain %s' % domain)
        cmd = '''echo -e '%s' > %s''' % ('\n'.join(s), config.RESOLV_CONF)
        return self._execute(cmd)

    def add_repo(self, *args):
        result = {}
        for repo in args:
            src = os.path.join(config.LOCAL_REPO_DIR, repo)
            dst = os.path.join(config.REMOTE_REPO_DIR, repo)
            result[repo] = self._upload(src, dst)
        return result

    def rm_repo(self, *args):
        return dict([
            (repo, self._execute('rm -rf %s' % os.path.join(config.REMOTE_REPO_DIR, repo)))for repo in args
        ])

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
            if not self._execute(cmd):
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
                if not self._execute(cmd):
                    continue
                result[username]['key_auth'] = True
            if user.sudo:
                result[username]['sudo'] = self._add_sudo(username)
        return result

    def rm_user(self, *args):
        return dict([
            (username, self._execute('''userdel -r -f %s''' % username)) for username in args
        ])

    def rm_sudo(self, *args):
        return dict([
            (username, self._execute('''gpasswd -d %s wheel''' % username)) for username in args
        ])

    def add_sudo(self, *args):
        return dict([
            (username, self._add_sudo(username)) for username in args
        ])

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
            result['security_login'] = self._execute(cmd)

        if root_key:
            cmd = '''mkdir -p {root_ssh_path}'''.format(root_ssh_path=Root.get_ssh_path())
            cmd += ''' && echo {content} > {root_authorized_keys}'''.format(
                    content=Root.get_key(),
                    root_authorized_keys=Root.get_authorized_keys_path()
            )
            cmd += ''' && chmod 600 {root_authorized_keys}'''.format(root_authorized_keys=Root.get_authorized_keys_path())
            result['root_key'] = self._execute(cmd)

        return result

    def optimize(self, ulimit=False, sysctl=False):
        result = {}

        if sysctl and self._upload(config.LOCAL_SYSCTL_FILE, '/tmp/init.py'):
            cmd = 'python /tmp/init.py && rm -rf /tmp/init.py'
            result['sysctl'] = self._execute(cmd)

        if ulimit:
            result['ulimit'] = self._upload(config.LOCAL_ULIMIT_CONF, config.REMOTE_ULIMIT_CONF)

        return result

    def services(self, install=None, modify=None, restart=None):
        result = {}

        if install:
            r = {}
            for service, params in install.iteritems():
                r[service] = False
                enable = params.get('enable', False)
                conf = params.get('config', {})
                svr = get_service(service, conf, self._upload, self._execute)
                if not svr:
                    continue
                r[service] = svr.install(enable, ip=self.server)
            result['install'] = r

        if modify:
            r = {}
            for service, params in modify.iteritems():
                r[service] = False
                update = params.get('update', False)
                conf = params.get('config', {})
                svr = get_service(service, conf, self._upload, self._execute)
                if not svr:
                    continue
                r[service] = svr.update(update, ip=self.server)
            result['modify'] = r

        if restart:
            result['restart'] = {}
            for service in restart:
                svr = get_service(service, {}, self._upload, self._execute)
                if not svr:
                    continue
                result['restart'][service] = svr.restart(ip=self.server)

        return result

