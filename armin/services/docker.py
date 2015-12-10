#!/usr/bin/python
#coding:utf-8

from armin import config
from armin.utils import copy_to_remote

class Docker(object):
    def __init__(self, config):
        eru = config.get('eru')
        pod = config.get('pod')
        ip = config.get('ip')
        if not pod or not eru:
            raise Exception('no params')
        self.pod = pod
        self.eru = eru
        self.ip = ip

    def make_service(self, uploader):
        return copy_to_remote(
                    uploader, config.DOCKER_SETUP,
                    ip=self.ip, eru=self.eru,
                    pod=self.pod, builder=config.DOCKER_GENERATOR) and \
                copy_to_remote(uploader, config.DOCKER_GENERATOR) and \
                copy_to_remote(uploader, config.DOCKER_NSENTER, config.REMOTE_BIN_DIR) and \
                copy_to_remote(uploader, config.DOCKER_ENTER, config.REMOTE_BIN_DIR)

