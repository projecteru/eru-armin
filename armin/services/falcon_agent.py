#!/usr/bin/python
#coding:utf-8

import os
import json
from armin import config
from armin.utils import make_remote_file

class FalconAgent(object):
    def __init__(self, params):
        if params is None:
            raise Exception('no params')
        self.params = params

    def make_service(self, uploader):
        p = os.path.join(config.LOCAL_SERVICES_DIR, config.FALCON_AGENT_CONF)
        with open(p) as fp:
            falcon_config = json.load(fp)
        for k, v in self.params.iteritems():
            if not falcon_config.get(k, None):
                continue
            if not isinstance(v, dict):
                falcon_config[k] = v
                continue
            for s, p in v.iteritems():
                falcon_config[k][s] = p
        rp = os.path.join(config.REMOTE_FALCON_AGENT_CONFIG_PATH, config.FALCON_AGENT_CONF)
        return make_remote_file(uploader, rp, json.dumps(falcon_config, indent=4))

