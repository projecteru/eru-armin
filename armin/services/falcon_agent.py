#!/usr/bin/python
#coding:utf-8

import os
import json
from armin import config
from armin.services import Service
from armin.utils import make_remote_file

class FalconAgent(Service):
    def install(self, enable=False, **kwargs):
        cmd = 'mkdir -p %s' % config.REMOTE_FALCON_AGENT_CONFIG_PATH
        if not self.executor(cmd):
            return False
        if not self.make_service():
            return False
        cmd = 'yum install falcon-agent -y && systemctl start falcon-agent'
        if enable:
            cmd += ' && systemctl enable falcon-agent'
        return self.executor(cmd)

    def update(self, update=False, **kwargs):
        if update and not self.params:
            cmd = 'systemctl stop falcon-agent && yum update falcon-agent -y && systemctl start falcon-agent'
            return self.executor(cmd)
        if not self.params:
            # nothing to do
            return True
        if not self.make_service():
            return False
        cmd = 'systemctl stop falcon-agent'
        if update:
            cmd += ' && yum update falcon-agent -y'
        cmd += ' && systemctl start falcon-agent'
        return self.executor(cmd)

    def make_service(self):
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
        return make_remote_file(self.uploader, rp, json.dumps(falcon_config, indent=4))

