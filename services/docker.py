#!/usr/bin/env python
# coding: utf-8

import os
import errno
import shutil
import subprocess
import tempfile

def call_command(cmd):
    return subprocess.call(cmd.split(' '))

def make_dir(path):
    try:
        os.mkdir(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

def make_file(path, content):
    with open(path, 'w') as f:
        f.write(content)
    os.chmod(path, 0644)

DOCKER_SERVER_TLS_PATH = '/etc/docker/tls'
DOCKER_CLIENT_TLS_PATH = '/root/.docker'

def install_docker_agent():
    # install docker and eru-agent rpm package
    print '---> install docker packages ...'
    call_command('yum -y install docker-engine')
    print '---> install docker packages done'

    # generate docker tls files
    print '---> generate docker tls certs ...'
    generate_certs()
    print '---> generate docker tls certs done'


class TempSpace(object):
    def __init__(self):
        path = tempfile.mkdtemp()
        self.current_path = self.path = os.path.expanduser(path)

    def __enter__(self):
        self.current_path = os.path.dirname(__file__)
        os.chdir(self.path)

    def __exit__(self, etype, value, tb):
        os.chdir(self.current_path)
        shutil.rmtree(self.path)

IP = '{ip}'
POD = '{pod}'
ERU = '{eru}'

def generate_certs():
    builder = os.path.join(os.getcwd(), 'certs')
    with TempSpace():
        call_command('sh %s %s %s' % (builder, IP, os.getcwd()))

        # copy server side certs
        make_dir(os.path.dirname(DOCKER_SERVER_TLS_PATH))
        make_dir(DOCKER_SERVER_TLS_PATH)
        [shutil.copy(cert, os.path.join(DOCKER_SERVER_TLS_PATH, cert)) for cert in ('ca.pem', 'server-key.pem', 'server-cert.pem')]

        # copy client side certs
        make_dir(DOCKER_CLIENT_TLS_PATH)
        [shutil.copy(cert, os.path.join(DOCKER_CLIENT_TLS_PATH, cert)) for cert in ('ca.pem', 'key.pem', 'cert.pem')]

def register_host():
    addr = '%s:2376' % IP
    pod_name = POD
    ca = os.path.join(DOCKER_CLIENT_TLS_PATH, 'ca.pem')
    key = os.path.join(DOCKER_CLIENT_TLS_PATH, 'key.pem')
    cert = os.path.join(DOCKER_CLIENT_TLS_PATH, 'cert.pem')
    url = 'http://%s/api/sys/host/create' % ERU
    cmd = 'curl -F addr=%s -F pod_name=%s -F ca=@%s -F key=@%s -F cert=@%s %s'
    cmd = cmd % (addr, pod_name, ca, key, cert, url)
    call_command(cmd)

if __name__ == '__main__':
    install_docker_agent()
    register_host()

