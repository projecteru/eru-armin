import logging
import importlib
from armin import config

logger = logging.getLogger(__name__)

def get_service(name, params, uploader, executor):
    mod_name = config.SERVICE_CLS_MAP.get(name, None)
    if not mod_name:
        return None
    mod, cls = mod_name.split('.')
    mod = importlib.import_module('armin.services.%s' % mod, 'armin.services')
    cls = getattr(mod, cls)
    if not cls:
        return None
    try:
        svr = cls(params, uploader, executor)
    except Exception, e:
        logger.exeception(e)
        return None
    return svr

class Service(object):
    def __init__(self, params, uploader, executor):
        self.params = params
        self.uploader = uploader
        self.executor = executor

    def install(self, enable=False, **kwargs):
        pass

    def update(self, update=False, **kwargs):
        pass

