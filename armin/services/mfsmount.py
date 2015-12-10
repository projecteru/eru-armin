#!/usr/bin/python
#coding:utf-8

from armin import config
from armin.utils import copy_to_remote

class MFSmount(object):
    def __init__(self, config):
        mfsmaster = config.get('mfsmaster')
        port = config.get('port')
        mount = config.get('mount')
        if not mfsmaster or not port or not mount:
            raise Exception('no params')
        self.mfsmaster = mfsmaster
        self.port = port
        self.mount = mount

    def make_service(self, uploader):
        return copy_to_remote(
            uploader, config.MOOSEFS_CLIENT_SERVICE, config.REMOTE_SERVICE_DIR,
            mfsmaster=self.mfsmaster, port=self.port, mount=self.mount,
        )

