#!/usr/bin/python
#coding:utf-8

import logging
import paramiko
from armin.host import Host

def ssh_client(server, user, password, keyfile, logger):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            server,
            username = user,
            password = password,
            key_filename = keyfile,
            look_for_keys = False,
        )
    except Exception, e:
        logger.exception(e)
    else:
        return Host(server, client, logger)


def generate_ssh_clients(config, logger):
    servers = config.get('servers')
    auth = config.get('auth')
    if not servers or not auth:
        return None
    clients = {}
    for server in servers:
        clients[server] = ssh_client(server, auth.get('user'), auth.get('password'), auth.get('keyfile'), logger)
    return clients


def generate_ssh_client(server, auth, logger):
    if not server or not auth:
        return None
    return ssh_client(server, auth['user'], auth['password'], auth['keyfile'], logger)


def resolve_servers(config):
    return config.get('servers')
