#!/usr/bin/python
#coding:utf-8

import os
from armin import config
from armin.utils import make_remote_file

class Docker(object):
    def __init__(self, config):
        eru = config.get('eru')
        pod = config.get('pod')
        ip = config.get('ip')
        if not pod or not eru:
            return False
        self.pod = pod
        self.eru = eru
        self.ip = ip

    def make_service(self, uploader):
        p = os.path.join(config.LOCAL_SERVICES_DIR, config.DOCKER_SETUP)
        rp = os.path.join(config.REMOTE_DOCKER_WORKDIR, config.DOCKER_SETUP)
        with open(p) as fp:
            content = fp.read().format(
                ip=self.ip, pod=self.pod, eru=self.eru, builder=config.DOCKER_GENERATOR
            )
        r1 = make_remote_file(uploader, rp, content)
        p = os.path.join(config.LOCAL_SERVICES_DIR, config.DOCKER_GENERATOR)
        rp = os.path.join(config.REMOTE_DOCKER_WORKDIR, config.DOCKER_GENERATOR)
        with open(p) as fp:
            content = fp.read()
        r2 = make_remote_file(uploader, rp, content)
        p = os.path.join(config.LOCAL_SERVICES_DIR, config.DOCKER_NSENTER)
        rp = os.path.join(config.REMOTE_BIN_DIR, config.DOCKER_NSENTER)
        with open(p) as fp:
            content = fp.read()
        r3 = make_remote_file(uploader, rp, content)
        p = os.path.join(config.LOCAL_SERVICES_DIR, config.DOCKER_ENTER)
        rp = os.path.join(config.REMOTE_BIN_DIR, config.DOCKER_ENTER)
        with open(p) as fp:
            content = fp.read()
        r4 = make_remote_file(uploader, rp, content)
        #TODO fix root bashrc
        return r1 and r2 and r3 and r4

