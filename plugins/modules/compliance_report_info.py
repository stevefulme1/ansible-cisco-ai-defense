# -*- coding: utf-8 -*-
# Copyright (c) 2024, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing Cisco AI Defense compliance reports."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: compliance_report_info
short_description: Retrieve compliance report information from Cisco AI Defense
description:
    - Retrieve compliance report information from Cisco AI Defense via the Cisco AI Defense REST API.
version_added: "1.0.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    report_id:
        description:
            - The report id parameter.
        type: str
        required: false
    api_url:
        description:
            - The Cisco AI Defense API endpoint URL.
        type: str
        required: true
    api_key:
        description:
            - The API key for authentication.
        type: str
        required: true
        no_log: true
    validate_certs:
        description:
            - Whether to validate SSL certificates.
        type: bool
        default: true
requirements:
    - "python >= 3.9"
    - "requests"
"""

EXAMPLES = r"""
- name: Retrieve compliance report information from cisco ai defense
  stevefulme1.cisco_ai_defense.compliance_report_info:
    report_id: "example-value"
"""

RETURN = r"""
compliance_reports:
    description: Details of the compliance reports.
    returned: On success.
    type: dict
"""

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

from ansible.module_utils.basic import AnsibleModule


def main():
    module_args = dict(
        report_id=dict(type="str"),
        api_url=dict(type="str", required=True),
        api_key=dict(type="str", required=True, no_log=True),
        validate_certs=dict(type="bool", default=True),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    api_url = module.params["api_url"].rstrip("/")
    headers = {
        "Authorization": f"Bearer {module.params['api_key']}",
        "Content-Type": "application/json",
    }

    try:
        url = f"{api_url}/api/v1/compliance_reports"
        response = requests.get(
            url,
            headers=headers,
            verify=module.params["validate_certs"],
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()
    except requests.RequestException as e:
        module.fail_json(msg=f"API request failed: {e}")

    module.exit_json(changed=False, compliance_reports=result)


if __name__ == "__main__":
    main()
