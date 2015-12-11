#!/usr/bin/python
#coding:utf-8

import os
from armin import config
from armin.services import Service
from armin.utils import load_config, dump_config, make_remote_file

class EruAgent(Service):
    def install(self, enable=False, **kwargs):
        cmd = 'mkdir -p %s' % config.REMOTE_ERU_AGENT_CONFIG_PATH
        if not self.executor(cmd):
            return False
        if not self.make_service():
            return False
        cmd = 'yum install eru-agent -y && systemctl start eru-agent'
        if enable:
            cmd += ' && systemctl enable eru-agent'
        return self.executor(cmd)

    def update(self, update=False, **kwargs):
        if update and not config:
            cmd = 'systemctl stop eru-agent && yum update eru-agent -y && systemctl start eru-agent'
            return self.executor(cmd)
        if not config:
            return True
        if not self.make_service():
            return False
        cmd = 'systemctl stop eru-agent'
        if update:
            cmd += ' && yum update eru-agent -y'
        cmd += ' && systemctl start eru-agent'
        return self.executor(cmd)

    def make_service(self):
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
                self.uploader, rp,
                dump_config(eru_config, default_flow_style=False)
        )

