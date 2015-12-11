#!/usr/bin/python
#coding:utf-8

from armin import config
from armin.utils import copy_to_remote
from armin.services import Service

class MFSmount(Service):
    def install(self, enable=False, **kwargs):
        if not self.make_service():
            return False
        cmd = 'yum install moosefs-client -y && mkdir -p %s && systemctl daemon-reload && systemctl start mfsmount' % self.params['mount']
        if enable:
            cmd += ' && systemctl enable mfsmount'
        return self.executor(cmd)

    def update(self, update=False, *kwargs):
        if update and not self.params:
            cmd = 'systemctl stop mfsmount && yum update moosefs-client -y && systemctl start mfsmount'
            return self.executor(cmd)
        if not self.params:
            # nothing to do
            return True
        if not self.make_service():
            return False
        cmd = 'systemctl stop mfsmount'
        if update:
            cmd += ' && yum update moosefs-client -y'
            # 保证有那个文件夹
            cmd += ' && mkdir -p %s && systemctl daemon-reload && systemctl start mfsmount' % self.params['mount']
        return self.executor(cmd)

    def make_service(self):
        mfsmaster = self.params.get('mfsmaster')
        port = self.params.get('port')
        mount = self.params.get('mount')
        if not mfsmaster or not port or not mount:
            return False
        return copy_to_remote(
            self.uploader, config.MOOSEFS_CLIENT_SERVICE,
            config.REMOTE_SERVICE_DIR,
            mfsmaster=mfsmaster, port=port, mount=mount,
        )

