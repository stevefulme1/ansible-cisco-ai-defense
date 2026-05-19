# -*- coding: utf-8 -*-
# Copyright (c) 2024, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module to retrieve validation results from Cisco AI Defense."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: validation_report_info
short_description: Retrieve validation run results from Cisco AI Defense
description:
    - Fetch the detailed report for a completed validation run, including
      per-category scores, benchmark comparisons, and individual findings.
    - Use after launching a validation run with the C(validation_run) module.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    validation_id:
        description:
            - The unique identifier of the validation run to retrieve results for.
        type: str
        required: true
    include_details:
        description:
            - Whether to include detailed per-finding information in the report.
            - Setting to C(false) returns only summary scores and benchmarks.
        type: bool
        default: true
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
- name: Retrieve full validation report with details
  stevefulme1.cisco_ai_defense.validation_report_info:
    validation_id: "val-abc-12345"
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"
  register: report

- name: Retrieve summary-only validation report
  stevefulme1.cisco_ai_defense.validation_report_info:
    validation_id: "val-abc-12345"
    include_details: false
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"

- name: Fail the playbook if validation did not pass
  stevefulme1.cisco_ai_defense.validation_report_info:
    validation_id: "{{ validation.validation.validation_id }}"
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"
  register: report
  failed_when: report.report.overall_status != 'passed'
"""

RETURN = r"""
report:
    description: The validation run report.
    returned: success
    type: dict
    contains:
        category_scores:
            description: Scores for each tested validation category.
            type: dict
            returned: always
        benchmark_comparison:
            description: Comparison of results against industry benchmarks.
            type: dict
            returned: always
        findings:
            description: List of individual findings from the validation run.
            type: list
            elements: dict
            returned: when include_details is true
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.cisco_ai_defense.plugins.module_utils.ai_defense import (
    AiDefenseClient,
)


def main():
    module_args = dict(
        validation_id=dict(type="str", required=True),
        include_details=dict(type="bool", default=True),
        api_url=dict(type="str", required=True),
        api_key=dict(type="str", required=True, no_log=True),
        validate_certs=dict(type="bool", default=True),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    client = AiDefenseClient(module)

    validation_id = module.params["validation_id"]
    params = {"include_details": module.params["include_details"]}

    result = client.get(
        f"/api/v1/validation/runs/{validation_id}/report",
        params=params,
    )

    if result is None:
        module.fail_json(
            msg=f"Validation run '{validation_id}' not found.",
        )

    module.exit_json(changed=False, report=result)


if __name__ == "__main__":
    main()
