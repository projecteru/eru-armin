#!/usr/bin/python
#coding:utf-8

import yaml
import random
from functools import partial
from collections import OrderedDict

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

load_config = partial(ordered_load, Loader=yaml.SafeLoader)

def get_random_passwd(string_length=8):
    return ''.join([random.choice(SETS) for _ in range(string_length)])
