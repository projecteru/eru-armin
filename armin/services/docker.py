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

    def prepare(self, uploader):
        p = os.path.join(config.LOCAL_SERVICES_DIR, config.DOCKER_SETUP)
        with open(p) as fp:
            content = fp.read().format(ip=self.ip, pod=self.pod, eru=self.eru)
        r1 = make_remote_file(uploader, '/tmp/dockersetup.py', content)
        p = os.path.join(config.LOCAL_SERVICES_DIR, config.DOCKER_GENERATOR)
        with open(p) as fp:
            content = fp.read()
        r2 = make_remote_file(uploader, '/tmp/certs', content)
        p = os.path.join(config.LOCAL_SERVICES_DIR, config.DOCKER_NSENTER)
        with open(p) as fp:
            content = fp.read()
        r3 = make_remote_file(uploader, '/usr/bin/nsenter', content)
        p = os.path.join(config.LOCAL_SERVICES_DIR, config.DOCKER_ENTER)
        with open(p) as fp:
            content = fp.read()
        r4 = make_remote_file(uploader, '/usr/bin/docker-enter', content)

        return r1 and r2 and r3 and r4

    def make_service(self, uploader):
        p = os.path.join(config.LOCAL_SERVICES_DIR, config.DOCKER_SERVICE)
        with open(p) as fp:
            content = fp.read()
        return  make_remote_file(uploader, config.DOCKER_REMOTE_PATH, content)

