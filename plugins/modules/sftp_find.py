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

requirements:
    pysftp>=0.2.9

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


def main():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type='path', required=True),
            pattern=dict(type='str', required=True),
            host=dict(type='str', required=True),
            port=dict(type='int', required=True),
            username=dict(type='str', required=True),
            password=dict(type='str', no_log=True, required=True)
        ),
        supports_check_mode=True
    )

    path = module.params['path']
    pattern = module.params['pattern']
    host = module.params['host']
    port = module.params['port']
    username = module.params['username']
    password = module.params['password']

    files_found = []
    file_names = []

    if not PARAMIKO_AVAILABLE:
        module.fail_json(msg=missing_required_lib("paramiko"), exception=LIB_IMP_ERR)

    #TODO: Connect function

    module.exit_json(files_found=files_found, file_names=file_names, changed=changed)


if __name__ == '__main__':
    main()
