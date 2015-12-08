#!/usr/bin/python
#coding:utf-8

INTERFACE_CONFIG = '/etc/sysconfig/network-scripts/ifcfg-%s'
GATEWAY_CONFIG = 'GATEWAY=%s'

RESOLV_CONF = '/etc/resolv.conf'
HOSTS_CONF = '/etc/hosts'

EXECUTE_EXCEPTION_CODE = -1
EXECUTE_OK = 0

LOCAL_REPO_DIR = '/Users/CMGS/Documents/Workplace/work/armin2/repos/'
REMOTE_REPO_DIR = '/etc/yum.repos.d/'

USERADD_BIN = 'adduser'
PKEY_DIR = '/Users/CMGS/Documents/Workplace/work/armin2/keys/'
REMOTE_HOME_DIR = '/home'

REMOTE_SSH_DIR = '.ssh'
REMOTE_AUTHORIZED_KEYS = 'authorized_keys'

LOGIN_SHELL = '/bin/bash'
NOLOGIN = '/sbin/nologin'

PASSWORD_LENGTH = 8
