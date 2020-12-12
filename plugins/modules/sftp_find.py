#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Konstantinos Georgoudis <kgeor@blacklines.gr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: sftp_find

short_description: sftp find module

version_added: "1.0.0"

description:
    - Return a list of files based on specific criteria on an sftp host
    - Multiple criteria are AND'd together

options:
    path:
        description:
            - The path on the remote sftp host where the files are
            - It can be full path, relative path, or a . for current path
        required: true
        type: path
    pattern:
        description:
            - You can choose a filename, or wildcard ending with file extension
            - E.g. filename.txt or *.csv or ADD_????????_export.csv
        type: str
        default: "*"
    host:
        description:
            - The IP address or the FQDN of the remote sftp host
        required: true
        type: str
    port:
        description:
            - The TCP port of the remote sftp host. The default port is 22
        type: int
        default: 22
    username:
        description:
            - Username for the sftp connection
        required: true
        type: str
    password:
        description:
            - Password for the sftp connection
        required: true
        type: str
    private_key:
        description:
            - Private key for the sftp connection
        required: false
        type: path

requirements:
    paramiko>=2.7.2

author:
    - Konstantinos Georgoudis (@tsimouha)
'''

EXAMPLES = r'''

- name: Find all csv files on the remote sftp host
  kgeor.sftp_modules.sftp_find:
    path: /some_path
    pattern: *.csv
    host: test.example.com
    port: 22
    username: demo
    password: somepassword
  delegate_to: localhost
  
'''

import fnmatch
import traceback
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import missing_required_lib

LIB_IMP_ERR = None
try:
    import paramiko

    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False
    LIB_IMP_ERR = traceback.format_exc()


def create_sftp_session(module, host, username, password, port, private_key_path, private_key_type):
    try:
        if private_key_path is not None:
            if private_key_path == 'DSA':
                key = paramiko.DSSKey.from_private_key_file(private_key_path)
            else:
                key = paramiko.RSAKey.from_private_key(private_key_path)
        else:
            password = password

        transport = paramiko.Transport(host, port)
        transport.connect(None, username, password, key)

        sftp = paramiko.SFTPClient.from_transport(transport)
        return sftp

    except Exception as e:
        module.fail_json(msg="Failed to connect on remote sftp host: %s" % e)
        if sftp is not None:
            sftp.close()
        if transport is not None:
            transport.close()
        pass


def main():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type='list', required=True, aliases=['name', 'path'], elements='str'),
            pattern=dict(type='str', required=True),
            host=dict(type='str', required=True),
            port=dict(type='int', required=True),
            username=dict(type='str', required=True),
            method=dict(type='str', choices=['password', 'private_key'], required=True),
            password=dict(type='str', no_log=True, required=True),
            private_key_path=dict(type='path', required=False),
            private_key_type=dict(type='str', choices=['DSA', 'RSA']),
        ),
        supports_check_mode=True,
        required_if=[
            ('method', 'password', 'password', True),
            ('method', 'private_key', ('private_key_path','private_key_type'), True),
        ],
    )

    params = module.params

    msg = ''
    looked = 0
    filelist = []

    path = params['path']
    pattern = params['pattern']
    host = params['host']
    port = params['port']
    username = params['username']
    password = params['password']
    private_key_path = params['private_key_path']
    private_key_type = params['private_key_type']

    if not PARAMIKO_AVAILABLE:
        module.fail_json(msg=missing_required_lib("paramiko"), exception=LIB_IMP_ERR)

    sftp = create_sftp_session(host, username, password, port, private_key_path, private_key_type)
    dirlist = sftp.listdir(path)
    for file in dirlist:
        filelist.append(file)

    module.exit_json(files=filelist, changed=False, msg=msg, examined=looked)


if __name__ == '__main__':
    main()
