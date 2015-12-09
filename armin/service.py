#!/usr/bin/python
#coding:utf-8

import logging
from armin import config

from armin.services import docker
from armin.services import mfsmount
from armin.services import falcon_agent

logger = logging.getLogger(__name__)


class Service(object):

    def __init__(self, host):
        self.host = host

    def restart(self, services):
        return dict([
            (service, self.host._execute('systemctl restart %s' % config.SERVICE_MAP[service])) for service in services
        ])

    def modify_moosefs_client(self, update=False, config=None):
        if update and not config:
            cmd = 'systemctl stop mfsmount && yum update moosefs-client -y && systemctl start mfsmount'
            return self.host._execute(cmd)
        if config:
            svr = mfsmount.MFSmount(config)
            if not svr:
                return False
            svr.make_service(self.host._upload)
            cmd = 'systemctl stop mfsmount'
            if update:
                cmd += ' && yum update moosefs-client -y'
            # 保证有那个文件夹
            cmd += ' && mkdir -p %s && systemctl daemon-reload && systemctl start mfsmount' % svr.mount
            return self.host._execute(cmd)
        return False

    def modify_falcon_agent(self, update=False, config=None):
        if update and not config:
            cmd = 'systemctl stop falcon-agent && yum update falcon-agent -y && systemctl start falcon-agent'
            return self.host._execute(cmd)
        if config:
            svr = falcon_agent.FalconAgent(config)
            if not svr:
                return False
            svr.make_service(self.host._upload)
            cmd = 'systemctl stop falcon-agent'
            if update:
                cmd += ' && yum update falcon-agent -y'
            cmd += ' && systemctl start falcon-agent'
            return self.host._execute(cmd)
        return False

    def install_moosefs_client(self, config, enable=False):
        svr = mfsmount.MFSmount(config)
        if not svr:
            return False
        svr.make_service(self.host._upload)
        cmd = 'yum install moosefs-client -y && mkdir -p %s && systemctl daemon-reload && systemctl start mfsmount' % svr.mount
        if enable:
            cmd += ' && systemctl enable mfsmount'
        return self.host._execute(cmd)

    def install_falcon_agent(self, config, enable=False):
        svr = falcon_agent.FalconAgent(config)
        if not svr:
            return False
        svr.make_service(self.host._upload)
        cmd = 'yum install falcon-agent -y && systemctl start falcon-agent'
        if enable:
            cmd += ' && systemctl enable falcon-agent'
        return self.host._execute(cmd)

    def install_docker(self, config, enable=False):
        config['ip'] = self.host.server
        svr = docker.Docker(config)
        if not svr:
            return False
        if not svr.prepare(self.host._upload):
            return False
        cmd = 'cd /tmp && python /tmp/dockersetup.py && rm -rf /tmp/dockersetup.py'
        if not self.host._execute(cmd):
            return False
        if not svr.make_service(self.host._upload):
            return False
        cmd = 'systemctl daemon-reload && systemctl start docker'
        cmd += ' && chmod +x /usr/bin/docker-enter && chmod +x /usr/bin/nsenter'
        if enable:
            cmd += ' && systemctl enable docker'
        return self.host._execute(cmd)

