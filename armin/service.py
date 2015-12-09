#!/usr/bin/python
#coding:utf-8

import logging
from armin import config

from armin.services.mfsmount import generate_mfsmount_service, upload_mfsmount_service

logger = logging.getLogger(__name__)


class Service(object):

    def __init__(self, host):
        self.host = host

    def restart(self, services):
        return dict([
            (service, self.host._execute('systemctl restart %s' % config.SERVICE_MAP[service])) for service in services
        ])

    def modify_moosefs_client(self, mfsmaster='mfsmaster', port=9521, mount='/mnt/mfs', update=False):
        content = generate_mfsmount_service(mfsmaster, port, mount)
        if not upload_mfsmount_service(self.host._upload, content):
            return False
        cmd = 'systemctl stop mfsmount'
        if update:
            cmd += ' && yum update moosefs-client -y'
        # 保证有那个文件夹
        cmd += ' && mkdir -p %s && systemctl daemon-reload && systemctl start mfsmount' % mount
        return self.host._execute(cmd)

    def install_moosefs_client(self, mfsmaster='mfsmaster', port=9521, mount='/mnt/mfs', enable=False):
        content = generate_mfsmount_service(mfsmaster, port, mount)
        if not upload_mfsmount_service(self.host._upload, content):
            return False
        cmd = 'yum install moosefs-client -y && mkdir -p %s && systemctl daemon-reload && systemctl start mfsmount' % mount
        if enable:
            cmd += ' && systemctl enable mfsmount'
        return self.host._execute(cmd)

