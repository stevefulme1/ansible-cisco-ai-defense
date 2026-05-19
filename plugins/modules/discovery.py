# -*- coding: utf-8 -*-
# Copyright (c) 2024, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module to trigger AI workload discovery scans in Cisco AI Defense."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: discovery
short_description: Trigger AI workload discovery scans in Cisco AI Defense
description:
    - Initiate discovery scans to identify AI models, agents, endpoints, and
      MCP servers running across cloud and on-premises environments.
    - Supports full, incremental, and targeted scan types to balance coverage
      with scan duration.
    - Results are added to the Cisco AI Defense asset inventory automatically.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    scan_type:
        description:
            - Type of discovery scan to execute.
            - C(full) scans all configured environments from scratch.
            - C(incremental) only scans for changes since the last full scan.
            - C(targeted) limits the scan to a specific cloud provider and region.
        type: str
        choices:
            - full
            - incremental
            - targeted
        required: true
    cloud_provider:
        description:
            - Restrict the scan to a specific cloud provider.
            - Required when I(scan_type=targeted).
        type: str
        required: false
    region:
        description:
            - Restrict the scan to a specific cloud region such as C(us-east-1).
            - Only used when I(cloud_provider) is also specified.
        type: str
        required: false
    state:
        description:
            - The desired state. Only C(present) is supported (triggers a scan).
        type: str
        choices:
            - present
        default: present
    api_url:
        description:
            - The Cisco AI Defense API endpoint URL.
        type: str
        required: true
    api_key:
        description:
            - The API key for authentication with Cisco AI Defense.
        type: str
        required: true
    validate_certs:
        description:
            - Whether to validate SSL/TLS certificates when connecting to the API.
        type: bool
        default: true
requirements:
    - "python >= 3.9"
    - "requests"
"""

EXAMPLES = r"""
- name: Run a full discovery scan across all environments
  stevefulme1.cisco_ai_defense.discovery:
    scan_type: full
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"

- name: Run an incremental scan to detect new assets
  stevefulme1.cisco_ai_defense.discovery:
    scan_type: incremental
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"

- name: Targeted scan of AWS us-east-1 region
  stevefulme1.cisco_ai_defense.discovery:
    scan_type: targeted
    cloud_provider: aws
    region: us-east-1
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"
"""

RETURN = r"""
scan:
    description: Details of the initiated discovery scan.
    returned: success
    type: dict
    contains:
        scan_id:
            description: Unique identifier for the discovery scan.
            type: str
            returned: always
        status:
            description: Current status of the scan (e.g. running, completed).
            type: str
            returned: always
        discovered_count:
            description: Number of AI assets discovered so far.
            type: int
            returned: always
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.cisco_ai_defense.plugins.module_utils.ai_defense import (
    AiDefenseClient,
)


def main():
    module_args = dict(
        scan_type=dict(
            type="str",
            required=True,
            choices=["full", "incremental", "targeted"],
        ),
        cloud_provider=dict(type="str"),
        region=dict(type="str"),
        state=dict(type="str", choices=["present"], default="present"),
        api_url=dict(type="str", required=True),
        api_key=dict(type="str", required=True, no_log=True),
        validate_certs=dict(type="bool", default=True),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    if module.check_mode:
        module.exit_json(changed=True)

    client = AiDefenseClient(module)

    payload = {"scan_type": module.params["scan_type"]}
    if module.params.get("cloud_provider"):
        payload["cloud_provider"] = module.params["cloud_provider"]
    if module.params.get("region"):
        payload["region"] = module.params["region"]

    result = client.post("/api/v1/discovery/scans", payload)
    module.exit_json(changed=True, scan=result)


if __name__ == "__main__":
    main()
