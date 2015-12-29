#!/usr/bin/python
#coding:utf-8

import os
from armin import config
from armin.services import Service
from armin.utils import load_config, dump_config, make_remote_file, copy_to_remote

class Registry(Service):
    def install(self, enable=False, **kwargs):
        cmd = 'mkdir -p %s' % config.REMOTE_REGISTRY_CONFIG_PATH
        if not self.executor(cmd) or not self.make_config() or not self.upload_service():
            return False
        cmd = 'cd {bindir} && adduser -d /data/registry -s /sbin/nologin -u 1000 -U registry && chmod +x {registry} && systemctl start {hub}'
        cmd = cmd.format(
            bindir = config.REMOTE_BIN_DIR,
            registry = config.REGISTRY_BIN,
            hub = config.REGISTRY_SERVICE,
        )
        if enable:
            cmd += ' && systemctl enable hub'
        return self.executor(cmd)

    def update(self, update=False, **kwargs):
        cmd = 'systemctl stop hub'
        if not self.executor(cmd) or not self.make_config():
            return False
        if not update:
            cmd = 'systemctl start hub'
            return self.executor(cmd)
        if not self.upload_service():
            return False
        cmd = 'systemctl daemon-reload && systemctl start hub'
        return self.executor(cmd)

    def make_config(self):
        p = os.path.join(config.LOCAL_SERVICES_DIR, config.REGISTRY_CONFIG_FILE)
        with open(p) as fp:
            registry_config = load_config(fp)
        for k, v in self.params.iteritems():
            if not registry_config.get(k, None):
                continue
            if not isinstance(v, dict):
                registry_config[k] = v
                continue
            for s, p in v.iteritems():
                registry_config[k][s] = p
        rp = os.path.join(config.REMOTE_REGISTRY_CONFIG_PATH, config.REGISTRY_CONFIG_FILE)
        return make_remote_file(
                self.uploader, rp,
                dump_config(registry_config, default_flow_style=False)
        )

    def upload_service(self):
        p = os.path.join(config.LOCAL_SERVICES_DIR, config.REGISTRY_SERVICE)
        with open(p) as fp:
            svr_unit = fp.read()
        svr_unit = svr_unit.format(
            registry_bin_path = os.path.join(config.REMOTE_BIN_DIR, config.REGISTRY_BIN),
            registry_config_path = os.path.join(config.REMOTE_REGISTRY_CONFIG_PATH, config.REGISTRY_CONFIG_FILE)
        )
        rp = os.path.join(config.REMOTE_SERVICE_DIR, config.REGISTRY_SERVICE)
        return make_remote_file(self.uploader, rp, svr_unit) and \
            copy_to_remote(self.uploader, config.REGISTRY_BIN, config.REMOTE_BIN_DIR)

