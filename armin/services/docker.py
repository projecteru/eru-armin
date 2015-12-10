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

    def _copy_to_remote(self, uploader, f, remote_dir=config.REMOTE_DOCKER_WORKDIR, **kwargs):
        local_path = os.path.join(config.LOCAL_SERVICES_DIR, f)
        remote_path = os.path.join(remote_dir, f)
        with open(local_path) as fp:
            if kwargs:
                content = fp.read().format(**kwargs)
            else:
                content = fp.read()
        return make_remote_file(uploader, remote_path, content)

    def make_service(self, uploader):
        return self._copy_to_remote(
                    uploader, config.DOCKER_SETUP,
                    ip=self.ip, eru=self.eru,
                    pod=self.pod, builder=config.DOCKER_GENERATOR) and \
                self._copy_to_remote(uploader, config.DOCKER_GENERATOR) and \
                self._copy_to_remote(uploader, config.DOCKER_NSENTER, config.REMOTE_BIN_DIR) and \
                self._copy_to_remote(uploader, config.DOCKER_ENTER, config.REMOTE_BIN_DIR)

