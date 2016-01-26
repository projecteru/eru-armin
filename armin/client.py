#!/usr/bin/python
#coding:utf-8

import logging
import paramiko
from armin.host import Host

logger = logging.getLogger(__name__)

def generate_ssh_clients(config):
    servers = config.get('servers')
    auth = config.get('auth')
    if not servers or not auth:
        return None
    clients = {}
    for server in servers:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(
                server,
                username = auth.get('user'),
                password = auth.get('password'),
                key_filename = auth.get('keyfile'),
                look_for_keys = False,
            )
        except Exception, e:
            logger.exception(e)
        else:
            clients[server] = Host(server, client)
    return clients


def generate_ssh_client(server, auth):
    if not server or not auth:
        return None

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            server,
            username = auth.get('user'),
            password = auth.get('password'),
            key_filename = auth.get('keyfile'),
            look_for_keys = False,
        )
    except Exception, e:
        logger.exception(e)
    else:
        host = Host(server, client)
    return host


def resolve_servers(config):
    servers = config.get('servers')
    return servers
