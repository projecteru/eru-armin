#!/usr/bin/python
#coding:utf-8

import logging
import importlib
from armin import config

logger = logging.getLogger(__name__)

def get_service(server, name, params, uploader, executor):
    mod_conf = config.SERVICE_CLS_MAP.get(name, None)
    if not mod_conf:
        return None
    mod_name = mod_conf['mod']
    service_name = mod_conf['unit']
    mod, cls = mod_name.split('.')
    mod = importlib.import_module('armin.services.%s' % mod, 'armin.services')
    cls = getattr(mod, cls)
    if not cls:
        return None
    try:
        svr = cls(server, service_name, params, uploader, executor)
    except Exception, e:
        logger.exeception(e)
        return None
    return svr

class Service(object):
    def __init__(self, server, service_name, params, uploader, executor):
        self.service_name = service_name
        self.params = params
        self.server = server
        self.uploader = uploader
        self.executor = executor

    def install(self, enable=False, **kwargs):
        pass

    def update(self, update=False, **kwargs):
        pass

    def restart(self):
        #TODO 足够简单
        return self.executor('systemctl restart %s' % self.service_name)
