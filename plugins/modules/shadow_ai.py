# -*- coding: utf-8 -*-
# Copyright (c) 2024, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module to detect unauthorized AI workloads via Cisco AI Defense."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: shadow_ai
short_description: Detect unauthorized shadow AI workloads with Cisco AI Defense
description:
    - Scan your environment for unauthorized or unmanaged AI workloads that
      may have been deployed outside of approved channels.
    - Shadow AI detection helps identify rogue models, unregistered agents,
      and unmonitored endpoints that pose security and compliance risks.
    - Optionally quarantine discovered shadow AI assets automatically.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    scan_scope:
        description:
            - Scope of the shadow AI detection scan.
            - C(full) scans both cloud and on-premises environments.
            - C(cloud_only) limits detection to cloud-hosted workloads.
            - C(on_prem_only) limits detection to on-premises infrastructure.
        type: str
        choices:
            - full
            - cloud_only
            - on_prem_only
        required: true
    auto_quarantine:
        description:
            - When set to C(true), automatically quarantine any shadow AI assets
              that are discovered during the scan.
            - Use with caution in production environments.
        type: bool
        default: false
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
- name: Detect shadow AI across all environments
  stevefulme1.cisco_ai_defense.shadow_ai:
    scan_scope: full
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"
  register: shadow_results

- name: Detect and quarantine unauthorized cloud AI workloads
  stevefulme1.cisco_ai_defense.shadow_ai:
    scan_scope: cloud_only
    auto_quarantine: true
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"

- name: Scan on-prem only for unauthorized models
  stevefulme1.cisco_ai_defense.shadow_ai:
    scan_scope: on_prem_only
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"
"""

RETURN = r"""
findings:
    description: List of shadow AI findings from the detection scan.
    returned: success
    type: list
    elements: dict
    contains:
        severity:
            description: Severity of the finding (critical, high, medium, low).
            type: str
            returned: always
        asset_name:
            description: Name or identifier of the unauthorized asset.
            type: str
            returned: always
        recommendation:
            description: Recommended remediation action.
            type: str
            returned: always
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.cisco_ai_defense.plugins.module_utils.ai_defense import (
    AiDefenseClient,
)


def main():
    module_args = dict(
        scan_scope=dict(
            type="str",
            required=True,
            choices=["full", "cloud_only", "on_prem_only"],
        ),
        auto_quarantine=dict(type="bool", default=False),
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

    payload = {
        "scan_scope": module.params["scan_scope"],
        "auto_quarantine": module.params["auto_quarantine"],
    }

    result = client.post("/api/v1/shadow_ai/detect", payload)
    findings = result if isinstance(result, list) else result.get("findings", [])
    module.exit_json(changed=True, findings=findings)


if __name__ == "__main__":
    main()
