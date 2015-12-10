#!/usr/bin/python
#coding:utf-8

import os
from armin import config
from armin.utils import load_config, dump_config, make_remote_file

class EruAgent(object):
    def __init__(self, params):
        if params is None:
            raise Exception('no params')
        self.params = params

    def make_service(self, uploader):
        p = os.path.join(config.LOCAL_SERVICES_DIR, config.ERU_AGENT_CONFIG_FILE)
        with open(p) as fp:
            eru_config = load_config(fp)
        for k, v in self.params.iteritems():
            if not eru_config.get(k, None):
                continue
            if not isinstance(v, dict):
                eru_config[k] = v
                continue
            for s, p in v.iteritems():
                eru_config[k][s] = p
        rp = os.path.join(config.REMOTE_ERU_AGENT_CONFIG_PATH, config.ERU_AGENT_CONFIG_FILE)
        return make_remote_file(
                uploader, rp,
                dump_config(eru_config, default_flow_style=False)
        )

