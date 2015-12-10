#!/usr/bin/python
#coding:utf-8

import os
import yaml
import random
from functools import partial
from collections import OrderedDict
from tempfile import NamedTemporaryFile

from armin import config

SETS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789~!@#$%^&*'

def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)

def ordered_dump(data, stream=None, Dumper=yaml.Dumper, **kwds):
    class OrderedDumper(Dumper):
        pass
    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())
    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)

dump_config = partial(ordered_dump, Dumper=yaml.SafeDumper)
load_config = partial(ordered_load, Loader=yaml.SafeLoader)

def get_random_passwd(string_length=8):
    return ''.join([random.choice(SETS) for _ in range(string_length)])

def make_remote_file(upload_func, remote_path, content):
    with NamedTemporaryFile('w') as f:
        f.write(content)
        f.flush()
        if not upload_func(f.name, remote_path):
            return False
    return True

def copy_to_remote(uploader, f, remote_dir=config.REMOTE_DOCKER_WORKDIR, **kwargs):
    local_path = os.path.join(config.LOCAL_SERVICES_DIR, f)
    remote_path = os.path.join(remote_dir, f)
    with open(local_path) as fp:
        if kwargs:
            content = fp.read().format(**kwargs)
        else:
            content = fp.read()
    return make_remote_file(uploader, remote_path, content)
