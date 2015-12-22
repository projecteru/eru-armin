#!/usr/bin/python
#coding:utf-8

from armin import config
from armin.services import Service
from armin.utils import copy_to_remote

class Calico(Service):
    def install(self, enable=False, **kwargs):
        self.params.update(kwargs)
        if not copy_to_remote(self.uploader, config.CALICOCTL, config.REMOTE_BIN_DIR):
            return False
        cmd = 'cd {bindir} && chmod +x {calicoctl}'.format(
            bindir=config.REMOTE_BIN_DIR, calicoctl=config.CALICOCTL
        )
        if not self.executor(cmd):
            return False
        etcd = self.params.get('etcd')
        ip = self.params.get('ip')
        if not etcd or not ip:
            return False
        image = self.params.get('image', 'calico/node')
        log = self.params.get('log', '/var/log/calico')
        cmd = 'docker pull %s' % image
        cmd += ' && export ETCD_AUTHORITY=%s' % etcd
        cmd += ' && calicoctl node --node-image=%s --log-dir=%s --ip=%s' % (image, log, ip)
        return self.executor(cmd)

    def update(self, update=False, **kwargs):
        pass

    def restart(self):
        raise NotImplementedError()
