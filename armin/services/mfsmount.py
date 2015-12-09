#!/usr/bin/python
#coding:utf-8

import os
from armin import config
from armin.utils import make_remote_file

class MFSmount(object):
    def __init__(self, config):
        mfsmaster = config.get('mfsmaster')
        port = config.get('port')
        mount = config.get('mount')
        if not mfsmaster or not port or not mount:
            return False
        self.mfsmaster = mfsmaster
        self.port = port
        self.mount = mount

    def make_service(self, uploader):
        p = os.path.join(config.LOCAL_SERVICES_DIR, config.MOOSEFS_CLIENT_SERVICE)
        with open(p) as fp:
            content = fp.read().format(mfsmaster=self.mfsmaster, port=self.port, mount=self.mount)
        return make_remote_file(uploader, config.MOOSEFS_CLIENT_REMOTE_PATH, content)

