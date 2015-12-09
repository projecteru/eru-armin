#!/usr/bin/python
#coding:utf-8

import os
import json
from armin import config
from armin.utils import make_remote_file

class FalconAgent(object):
    def __init__(self, config):
        hbs = config.get('hbs')
        transfer = config.get('transfer')
        if not hbs or not transfer:
            return False
        self.hbs = hbs
        self.transfer = transfer

    def make_service(self, uploader):
        p = os.path.join(config.LOCAL_SERVICES_DIR, config.FALCON_AGENT_CONF)
        with open(p) as fp:
            content = json.load(fp)
            content['heartbeat']['addr'] = self.hbs
            content['transfer']['addr'] = self.transfer
        return make_remote_file(uploader, config.FALCON_AGENT_REMOTE_PATH, json.dumps(content, indent=4))

