# -*- coding: utf-8 -*-
# Copyright (c) 2024, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for retrieving supply chain reports from Cisco AI Defense."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: supply_chain_report_info
short_description: Retrieve AI model supply chain reports from Cisco AI Defense
description:
    - Query supply chain security reports for AI models registered in Cisco AI Defense.
    - Reports cover provenance verification, dependency scanning, and integrity
      validation of model artefacts.
    - This is a read-only module that never modifies state.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    report_id:
        description:
            - Retrieve a single report by its unique identifier.
            - When omitted, returns a list of reports matching the other filters.
        type: str
    model_reference:
        description:
            - Filter reports to those associated with a specific model name or
              reference identifier.
        type: str
    status:
        description:
            - Filter reports by their completion status.
        type: str
        choices:
            - completed
            - in_progress
            - failed
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
- name: Retrieve all completed supply chain reports
  stevefulme1.cisco_ai_defense.supply_chain_report_info:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    status: completed
  register: completed_reports

- name: Get a specific report by ID
  stevefulme1.cisco_ai_defense.supply_chain_report_info:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    report_id: "rpt-abc123"
  register: single_report

- name: List reports for a specific model
  stevefulme1.cisco_ai_defense.supply_chain_report_info:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    model_reference: "gpt-4-internal-v2"
  register: model_reports

- name: List all supply chain reports
  stevefulme1.cisco_ai_defense.supply_chain_report_info:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
  register: all_reports
"""

RETURN = r"""
reports:
    description: List of supply chain report objects.
    returned: always
    type: list
    elements: dict
    contains:
        id:
            description: Unique report identifier.
            type: str
            returned: always
        model_reference:
            description: The model this report pertains to.
            type: str
            returned: always
        status:
            description: Report completion status.
            type: str
            returned: always
        created_at:
            description: Timestamp when the report was initiated.
            type: str
            returned: always
        findings:
            description: Summary of supply chain findings.
            type: dict
            returned: when status is completed
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.cisco_ai_defense.plugins.module_utils.ai_defense import (
    AiDefenseClient,
)


def main():
    module_args = dict(
        report_id=dict(type="str"),
        model_reference=dict(type="str"),
        status=dict(type="str", choices=["completed", "in_progress", "failed"]),
        api_url=dict(type="str", required=True),
        api_key=dict(type="str", required=True, no_log=True),
        validate_certs=dict(type="bool", default=True),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    client = AiDefenseClient(module)

    report_id = module.params.get("report_id")

    if report_id:
        result = client.get(f"/api/v1/supply_chain/reports/{report_id}")
        if result is None:
            module.fail_json(msg=f"Report not found: {report_id}")
        module.exit_json(changed=False, reports=[result])
    else:
        params = {}
        if module.params.get("model_reference"):
            params["model_reference"] = module.params["model_reference"]
        if module.params.get("status"):
            params["status"] = module.params["status"]

        result = client.get("/api/v1/supply_chain/reports", params=params)
        reports = result if isinstance(result, list) else result.get("reports", [])
        module.exit_json(changed=False, reports=reports)


if __name__ == "__main__":
    main()
