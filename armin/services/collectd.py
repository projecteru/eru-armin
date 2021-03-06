#!/usr/bin/python
#coding:utf-8

#sed -i 's/#Hostname    "localhost"/Hostname    "'$HOSTNAME'"'/g'
#sed -i 's/#LoadPlugin conntrack/LoadPlugin conntrack/g'
#sed -i 's/#LoadPlugin disk/LoadPlugin disk/g'

import os
import jinja2
from armin import config
from armin.services import Service
from armin.utils import make_remote_file

class Collectd(Service):
    def install(self, enable=False, **kwargs):
        cmds = [
            'yum install collectd -y',
            '''sed -i 's/#Hostname    "localhost"/Hostname    "'$HOSTNAME'"'/g /etc/collectd.conf ''',
            '''sed -i 's/#LoadPlugin conntrack/LoadPlugin conntrack/g' /etc/collectd.conf ''',
            '''sed -i 's/#LoadPlugin disk/LoadPlugin disk/g' /etc/collectd.conf ''',
        ]
        if not self.install_svr(cmds):
            return False
        self.make_service()
        cmd = 'systemctl start collectd'
        if enable:
            cmd += ' && systemctl enable collectd'
        return self.executor(cmd)

    def update(self, update=False, **kwargs):
        pass

    def install_svr(self, cmds):
        for cmd in cmds:
            if not self.executor(cmd):
                return False
        return True

    def make_service(self):
        confs_dir = os.path.join(config.LOCAL_SERVICES_DIR, config.COLLECTD_DIR)
        for plugin, params in self.params.iteritems():
            f_name = '%s.conf' % plugin
            path = os.path.join(confs_dir, f_name)
            if not os.path.exists(path):
                continue
            with open(path) as f:
                content = jinja2.Template(f.read()).render(params=params)
            rp = os.path.join(config.COLLECTD_REMOTE_DIR, f_name)
            if not make_remote_file(self.uploader, rp, content):
                print 'upload failed', f_name, rp
