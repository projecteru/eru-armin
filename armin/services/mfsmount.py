#!/usr/bin/python
#coding:utf-8

import os
from armin import config
from tempfile import NamedTemporaryFile

def generate_mfsmount_service(mfsmaster, port, mount):
    p = os.path.join(config.LOCAL_SERVICES_DIR, config.MOOSEFS_CLIENT_SERVICE)
    with open(p) as fp:
        return fp.read().format(mfsmaster=mfsmaster, port=port, mount=mount)

def upload_mfsmount_service(upload_func, content):
    with NamedTemporaryFile('w') as f:
        p = os.path.join(config.REMOTE_SERVICES_DIR, config.MOOSEFS_CLIENT_SERVICE)
        f.write(content)
        f.flush()
        if not upload_func(f.name, p):
            return False
    return True

