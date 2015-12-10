#!/usr/bin/python
#coding:utf-8

import logging

from armin import config as armin_config
from armin.services import docker
from armin.services import mfsmount
from armin.services import eru_agent
from armin.services import falcon_agent

from armin.services import get_service

logger = logging.getLogger(__name__)


class Service(object):

    def __init__(self, host):
        self.host = host

    def restart(self, services):
        return dict([
            (service, self.host._execute('systemctl restart %s' % armin_config.SERVICE_MAP[service])) for service in services
        ])

    def modify_moosefs_client(self, update=False, config=None):
        if update and not config:
            cmd = 'systemctl stop mfsmount && yum update moosefs-client -y && systemctl start mfsmount'
            return self.host._execute(cmd)
        if config:
            svr = get_service(mfsmount.MFSmount, config)
            if not svr:
                return False
            if not svr.make_service(self.host._upload):
                return False
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
            svr = get_service(falcon_agent.FalconAgent, config)
            if not svr:
                return False
            if not svr.make_service(self.host._upload):
                return False
            cmd = 'systemctl stop falcon-agent'
            if update:
                cmd += ' && yum update falcon-agent -y'
            cmd += ' && systemctl start falcon-agent'
            return self.host._execute(cmd)
        return False

    def modify_docker(self, update, config=None):
        #TODO config useless
        if not update:
            return True
        cmd = 'yum update docker-engine -y && systemctl restart docker'
        return self.host._execute(cmd)

    def modify_eru_agent(self, update=False, config=None):
        if update and not config:
            cmd = 'systemctl stop eru-agent && yum update eru-agent -y && systemctl start eru-agent'
            return self.host._execute(cmd)
        if config:
            svr = get_service(eru_agent.EruAgent, config)
            if not svr:
                return False
            if not svr.make_service(self.host._upload):
                return False
            cmd = 'systemctl stop eru-agent'
            if update:
                cmd += ' && yum update eru-agent -y'
            cmd += ' && systemctl start eru-agent'
            return self.host._execute(cmd)
        return False

    def install_moosefs_client(self, config, enable=False):
        svr = get_service(mfsmount.MFSmount, config)
        if not svr:
            return False
        if not svr.make_service(self.host._upload):
            return False
        cmd = 'yum install moosefs-client -y && mkdir -p %s && systemctl daemon-reload && systemctl start mfsmount' % svr.mount
        if enable:
            cmd += ' && systemctl enable mfsmount'
        return self.host._execute(cmd)

    def install_falcon_agent(self, config, enable=False):
        svr = get_service(falcon_agent.FalconAgent, config)
        if not svr:
            return False
        cmd = 'mkdir -p %s' % armin_config.REMOTE_FALCON_AGENT_CONFIG_PATH
        if not self.host._execute(cmd):
            return False
        if not svr.make_service(self.host._upload):
            return False
        cmd = 'yum install falcon-agent -y && systemctl start falcon-agent'
        if enable:
            cmd += ' && systemctl enable falcon-agent'
        return self.host._execute(cmd)

    def install_docker(self, config, enable=False):
        config['ip'] = self.host.server
        svr = get_service(docker.Docker, config)
        if not svr:
            return False
        if not svr.make_service(self.host._upload):
            return False
        cmd = 'cd {workdir} && python {setup} && rm -rf {setup} {certs}'
        cmd = cmd.format(
            workdir = armin_config.REMOTE_DOCKER_WORKDIR,
            setup = armin_config.DOCKER_SETUP,
            certs = armin_config.DOCKER_GENERATOR,
        )
        if not self.host._execute(cmd):
            return False
        cmd = 'cd {bindir} && chmod +x {docker_enter} && chmod +x {nsenter}'
        cmd = cmd.format(
            bindir = armin_config.REMOTE_BIN_DIR,
            docker_enter = armin_config.DOCKER_ENTER,
            nsenter = armin_config.DOCKER_NSENTER,
        )
        if enable:
            cmd += ' && systemctl enable docker'
        return self.host._execute(cmd)

    def install_eru_agent(self, config, enable=False):
        svr = get_service(eru_agent.EruAgent, config)
        if not svr:
            return False
        cmd = 'mkdir -p %s' % armin_config.REMOTE_ERU_AGENT_CONFIG_PATH
        if not self.host._execute(cmd):
            return False
        if not svr.make_service(self.host._upload):
            return False
        cmd = 'yum install eru-agent -y && systemctl start eru-agent'
        if enable:
            cmd += ' && systemctl enable eru-agent'
        return self.host._execute(cmd)

