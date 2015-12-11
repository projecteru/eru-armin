#!/usr/bin/python
#coding:utf-8

from armin import config
from armin.services import Service
from armin.utils import copy_to_remote

class Docker(Service):
    def install(self, enable=False, **kwargs):
        self.params.update(kwargs)
        if not self.make_service():
            return False
        cmd = 'cd {workdir} && python {setup} && rm -rf {setup} {certs}'
        cmd = cmd.format(
            workdir = config.REMOTE_DOCKER_WORKDIR,
            setup = config.DOCKER_SETUP,
            certs = config.DOCKER_GENERATOR,
        )
        if not self.executor(cmd):
            return False
        cmd = 'cd {bindir} && chmod +x {docker_enter} && chmod +x {nsenter}'
        cmd = cmd.format(
            bindir = config.REMOTE_BIN_DIR,
            docker_enter = config.DOCKER_ENTER,
            nsenter = config.DOCKER_NSENTER,
        )
        if enable:
            cmd += ' && systemctl enable docker'
        return self.executor(cmd)

    def update(self, update=False, **kwargs):
        if not update:
            return True
        cmd = 'yum update docker-engine -y && systemctl restart docker'
        return self.executor(cmd)

    def make_service(self):
        eru = self.params.get('eru')
        pod = self.params.get('pod')
        ip = self.params.get('ip')
        if not eru or not pod or not ip:
            return False
        return copy_to_remote(
                    self.uploader,
                    config.DOCKER_SETUP,
                    ip=ip, eru=eru,
                    pod=pod, builder=config.DOCKER_GENERATOR) and \
                copy_to_remote(self.uploader, config.DOCKER_GENERATOR) and \
                copy_to_remote(self.uploader, config.DOCKER_NSENTER, config.REMOTE_BIN_DIR) and \
                copy_to_remote(self.uploader, config.DOCKER_ENTER, config.REMOTE_BIN_DIR)

