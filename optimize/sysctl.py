#!/usr/bin/env python
# coding: utf-8

sysctl_conf = '''
# Controls IP packet forwarding
net.ipv4.ip_forward = 1

# Controls source route verification
net.ipv4.conf.default.rp_filter = 1

# Do not accept source routing
net.ipv4.conf.default.accept_source_route = 0

# Controls the System Request debugging functionality of the kernel
kernel.sysrq = 0

# Controls whether core dumps will append the PID to the core filename.
# Useful for debugging multi-threaded applications.
kernel.core_uses_pid = 1

# Controls the use of TCP syncookies
net.ipv4.tcp_syncookies = 1

# Disable netfilter on bridges.
# net.bridge.bridge-nf-call-ip6tables = 0
# net.bridge.bridge-nf-call-iptables = 0
# net.bridge.bridge-nf-call-arptables = 0

# Controls the default maxmimum size of a mesage queue
kernel.msgmnb = 65536

# Controls the maximum size of a message, in bytes
kernel.msgmax = 65536

# Controls the maximum shared segment size, in bytes
kernel.shmmax = 68719476736
kernel.shmall = 4294967296

#net.ipv4.tcp_mem = 14680064 15728640 16515072
net.ipv4.tcp_mem = {min_tcp_mem} {mid_tcp_mem} {max_tcp_mem}
net.ipv4.tcp_rmem = 4096 4096 16777216
net.ipv4.tcp_wmem = 4096 4096 16777216
net.ipv4.tcp_no_metrics_save = 1
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_tw_recycle = 1
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_timestamps = 1
net.nf_conntrack_max = 6553600
net.netfilter.nf_conntrack_max = 6553600
#tcp_tw_recycle = 0

vm.min_free_kbytes = 65536
vm.overcommit_memory = 1
net.ipv4.tcp_keepalive_time = 1200
net.ipv4.ip_local_port_range = 6000 65000
net.ipv4.tcp_max_syn_backlog = 8192
net.ipv4.tcp_max_tw_buckets = 100000
net.ipv4.tcp_synack_retries = 2
net.ipv4.tcp_syn_retries = 2
net.ipv4.tcp_max_orphans = 3276800

net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.core.netdev_max_backlog = 32768
net.core.somaxconn = 32768

# file
fs.file-max = 6513989
fs.nr_open = 10000000
'''

import os
import shutil
import subprocess
from datetime import datetime

def now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def call_command(cmd):
    return subprocess.call(cmd.split(' '))

def make_file(path, content):
    with open(path, 'w') as f:
        f.write(content)
    os.chmod(path, 0644)

def init_kernel():
    print '---> init kernel parameters ...'
    total_mem_kb = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / 1024
    max_tcp_mem = int(total_mem_kb * 0.9 / 4)
    mid_tcp_mem = int(total_mem_kb * 0.7 / 4)
    min_tcp_mem = int(total_mem_kb * 0.2 / 4)

    call_command('modprobe nf_conntrack')

    content = sysctl_conf.format(min_tcp_mem=min_tcp_mem, mid_tcp_mem=mid_tcp_mem, max_tcp_mem=max_tcp_mem)
    shutil.copy('/etc/sysctl.conf', '/etc/sysctl.conf.backup.%s' % now())
    make_file('/etc/sysctl.conf', content)

    call_command('sysctl -p')
    shutil.copy('/etc/security/limits.conf', '/etc/security/limits.conf.backup.%s' % now())
    print '---> init kernel parameters done'

def set_journald():
    call_command('mkdir /var/log/journal')
    call_command('systemd-tmpfiles --create --prefix /var/log/journal')
    call_command('systemctl restart systemd-journald')

if __name__ == '__main__':
    init_kernel()
    set_journald()

