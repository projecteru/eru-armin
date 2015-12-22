#!/usr/bin/env python
# coding: utf-8

import os
import time
import errno
import shutil
import subprocess
import tempfile

SERVICE_UNIT = '''
[Unit]
Description=Docker Application Container Engine
Documentation=https://docs.docker.com
After=network.target docker.socket
Requires=docker.socket

[Service]
Type=notify
ExecStart=/usr/bin/docker daemon -H fd:// -H tcp://0.0.0.0:2376 --tlsverify --tlscacert=/etc/docker/tls/ca.pem --tlscert=/etc/docker/tls/server-cert.pem --tlskey=/etc/docker/tls/server-key.pem --insecure-registry {hub}
MountFlags=slave
LimitNOFILE=10485760
LimitNPROC=10485760
LimitCORE=infinity

[Install]
WantedBy=multi-user.target
'''

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
DOCKER_SERVICE = '/usr/lib/systemd/system/docker.service'

def install_docker():
    # install docker and eru-agent rpm package
    print '---> install docker packages ...'
    call_command('yum -y install docker-engine')
    print '---> install docker packages done'

    print '---> copy service unit ...'
    make_file(DOCKER_SERVICE, SERVICE_UNIT)
    call_command('systemctl daemon-reload')
    print '---> copy service unit done'

    print '---> init data'
    call_command('rm -rf /var/lib/docker')
    call_command('mkdir -p /var/lib/docker/devicemapper/devicemapper')
    call_command('mkdir -p /data/docker')
    call_command('dd if=/dev/zero of=/data/docker/data bs=1G count=0 seek={data}')
    call_command('dd if=/dev/zero of=/data/docker/meta bs=1G count=0 seek={meta}')
    call_command('ln -s /data/docker/* /var/lib/docker/devicemapper/devicemapper/')
    print '---> init data done'

    # generate docker tls files
    print '---> generate docker tls certs ...'
    generate_certs()
    print '---> generate docker tls certs done'

    # start docker
    print '---> start docker ...'
    call_command('systemctl start docker')
    # fuck
    count = 0
    while count < 6:
        print '---> wait for docker start'
        time.sleep(1)
        count += 1
    print '---> start docker done ...'

class TempSpace(object):
    def __init__(self):
        path = tempfile.mkdtemp()
        self.path = os.path.expanduser(path)

    def __enter__(self):
        self.current_path = os.getcwd()
        os.chdir(self.path)

    def __exit__(self, etype, value, tb):
        os.chdir(self.current_path)
        shutil.rmtree(self.path)

IP = '{ip}'
POD = '{pod}'
ERU = '{eru}'
BUILDER = '{builder}'

def generate_certs():
    builder = os.path.join(os.getcwd(), BUILDER)
    with TempSpace():
        call_command('sh %s %s %s' % (builder, IP, os.getcwd()))

        # copy server side certs
        make_dir(os.path.dirname(DOCKER_SERVER_TLS_PATH))
        make_dir(DOCKER_SERVER_TLS_PATH)
        [shutil.copy(cert, os.path.join(DOCKER_SERVER_TLS_PATH, cert)) for cert in ('ca.pem', 'server-key.pem', 'server-cert.pem')]

        # copy client side certs
        make_dir(DOCKER_CLIENT_TLS_PATH)
        [shutil.copy(cert, os.path.join(DOCKER_CLIENT_TLS_PATH, cert)) for cert in ('ca.pem', 'key.pem', 'cert.pem')]

    call_command('systemctl start docker')

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
    install_docker()
    register_host()

