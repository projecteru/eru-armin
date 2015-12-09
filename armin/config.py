#!/usr/bin/python
#coding:utf-8

INTERFACE_CONFIG = '/etc/sysconfig/network-scripts/ifcfg-%s'
GATEWAY_CONFIG = 'GATEWAY=%s'

RESOLV_CONF = '/etc/resolv.conf'
HOSTS_CONF = '/etc/hosts'

EXECUTE_OK = 0

LOCAL_REPO_DIR = '/Users/CMGS/Documents/Workplace/work/armin2/repos/'
REMOTE_REPO_DIR = '/etc/yum.repos.d/'

USERADD_BIN = 'adduser'
PKEY_DIR = '/Users/CMGS/Documents/Workplace/work/armin2/keys/'
REMOTE_HOME_DIR = '/home'
REMOTE_NOLOGIN_HOME_DIR = '/var/lib'

REMOTE_SSH_DIR = '.ssh'
REMOTE_AUTHORIZED_KEYS = 'authorized_keys'

LOGIN_SHELL = '/bin/bash'
NOLOGIN = '/sbin/nologin'

SSHD_CONFIG = '/etc/ssh/sshd_config'

PASSWORD_LENGTH = 8

ARMIN_PUB_KEY = '/Users/CMGS/Documents/Workplace/work/armin2/root/root.pub'

LOCAL_ULIMIT_CONF = '/Users/CMGS/Documents/Workplace/work/armin2/optimize/limits.conf'
REMOTE_ULIMIT_CONF = '/etc/security/limits.conf'
LOCAL_SYSCTL_FILE = '/Users/CMGS/Documents/Workplace/work/armin2/optimize/sysctl.py'

REMOTE_SERVICES_DIR = '/usr/lib/systemd/system/'
LOCAL_SERVICES_DIR = '/Users/CMGS/Documents/Workplace/work/armin2/services'
MOOSEFS_CLIENT_SERVICE = 'mfsmount.service'

SERVICE_MAP = {
    'moosefs-client': 'mfsmount'
}


