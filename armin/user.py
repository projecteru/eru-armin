#!/usr/bin/python
#coding:utf-8

import os
from armin import config, utils

class User(object):

    def __init__(self, username, uid, login=True, sudo=False, pkey=None):
        self.username = username
        self.uid = uid
        self.sudo = sudo
        self.pkey = pkey
        self.login = login

    def get_key(self):
        if not self.pkey:
            return ''
        path = os.path.join(config.PKEY_DIR, self.pkey)
        with open(path) as f:
            content = f.readline()
        return content.strip()

    def get_shell(self):
        if not self.login:
            return config.NOLOGIN
        return config.LOGIN_SHELL

    def get_password(self, length=config.PASSWORD_LENGTH):
        return utils.get_random_passwd(length)

    def get_home(self):
        if self.login:
            return os.path.join(config.REMOTE_HOME_DIR, self.username)
        return os.path.join(config.REMOTE_NOLOGIN_HOME_DIR, self.username)

    def get_ssh_path(self):
        return os.path.join(self.get_home(), config.REMOTE_SSH_DIR)

    def get_authorized_keys_path(self):
        return os.path.join(self.get_ssh_path(), config.REMOTE_AUTHORIZED_KEYS)

class Root(object):

    @classmethod
    def get_key(cls):
        with open(config.ARMIN_PUB_KEY) as f:
            content = f.readline()
        return content.strip()

    @classmethod
    def get_ssh_path(cls):
        return '/root/.ssh'

    @classmethod
    def get_authorized_keys_path(cls):
        return '/root/.ssh/authorized_keys'

