#!/usr/bin/python
#coding:utf-8

import os

BASE_PATH = os.getcwd()

INTERFACE_CONFIG = '/etc/sysconfig/network-scripts/ifcfg-%s'
GATEWAY_CONFIG = 'GATEWAY=%s'

RESOLV_CONF = '/etc/resolv.conf'
HOSTS_CONF = '/etc/hosts'

EXECUTE_OK = 0

LOCAL_REPO_DIR = os.path.join(BASE_PATH, 'repos')
REMOTE_REPO_DIR = '/etc/yum.repos.d/'

USERADD_BIN = 'adduser'
PKEY_DIR = os.path.join(BASE_PATH, 'keys')
REMOTE_HOME_DIR = '/home'
REMOTE_NOLOGIN_HOME_DIR = '/var/lib'

REMOTE_SSH_DIR = '.ssh'
REMOTE_AUTHORIZED_KEYS = 'authorized_keys'

LOGIN_SHELL = '/bin/bash'
NOLOGIN = '/sbin/nologin'

SSHD_CONFIG = '/etc/ssh/sshd_config'

PASSWORD_LENGTH = 8

ARMIN_PUB_KEY = os.path.join(BASE_PATH, 'root', 'root.pub')

LOCAL_ULIMIT_CONF = os.path.join(BASE_PATH, 'optimize', 'limits.conf')
LOCAL_SYSCTL_FILE = os.path.join(BASE_PATH, 'optimize', 'sysctl.py')
REMOTE_ULIMIT_CONF = '/etc/security/limits.conf'

LOCAL_SERVICES_DIR = os.path.join(BASE_PATH, 'services')

FALCON_AGENT_CONF = 'cfg.json'
MOOSEFS_CLIENT_SERVICE = 'mfsmount.service'
COLLECTD_DIR = 'collectd'
COLLECTD_REMOTE_DIR = '/etc/collectd.d/'

DOCKER_SETUP = 'docker.py'
DOCKER_GENERATOR = 'certs'
DOCKER_NSENTER = 'nsenter'
DOCKER_ENTER = 'docker-enter'

CALICOCTL = 'calicoctl'

ERU_AGENT_CONFIG_FILE = 'agent.yaml'

REMOTE_DOCKER_WORKDIR = '/tmp'
REMOTE_BIN_DIR = '/usr/bin'
REMOTE_SERVICE_DIR = '/usr/lib/systemd/system'

REMOTE_ERU_AGENT_CONFIG_PATH = '/etc/eru-agent/'
REMOTE_FALCON_AGENT_CONFIG_PATH = '/etc/falcon-agent/'
REMOTE_REGISTRY_CONFIG_PATH = '/etc/registry/'

REGISTRY_CONFIG_FILE = 'registry.yaml'
REGISTRY_BIN = 'registry'
REGISTRY_SERVICE = 'hub.service'

SERVICE_CLS_MAP = {
    'moosefs-client': {
        'mod': 'mfsmount.MFSmount', 'unit': 'mfsmount',
    },
    'falcon-agent': {
        'mod': 'falcon_agent.FalconAgent', 'unit': 'falcon-agent',
    },
    'docker': {
        'mod': 'docker.Docker', 'unit': 'docker',
    },
    'eru-agent': {
        'mod': 'eru_agent.EruAgent', 'unit': 'eru-agent',
    },
    'calico': {
        'mod': 'calico.Calico', 'unit': 'calico',
    },
    'registry': {
        'mod': 'registry.Registry', 'unit': 'hub',
    },
    'collectd': {
        'mod': 'collectd.Collectd', 'unit': 'collectd',
    },
}

try:
    from local_config import *
except ImportError:
    pass
