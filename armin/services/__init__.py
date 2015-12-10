import logging

logger = logging.getLogger(__name__)

def get_service(cls, config):
    try:
        svr = cls(config)
    except Exception, e:
        logger.exeception(e)
        return None
    else:
        return svr

