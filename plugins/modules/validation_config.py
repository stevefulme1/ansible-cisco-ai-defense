# -*- coding: utf-8 -*-
# Copyright (c) 2024, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module to manage validation configurations in Cisco AI Defense."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: validation_config
short_description: Configure validation parameters in Cisco AI Defense
description:
    - Create, update, or delete validation configurations that define which
      categories to test, pass thresholds, and report formats.
    - Validation configs are reusable templates that can be referenced by
      validation runs and schedules.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    name:
        description:
            - Name of the validation configuration.
        type: str
        required: true
    categories:
        description:
            - List of validation categories to include in this configuration.
            - Examples include C(prompt_injection), C(data_leakage),
              C(harmful_content), C(bias), and C(compliance).
        type: list
        elements: str
        required: true
    pass_threshold:
        description:
            - Minimum score (0.0 to 1.0) required for a validation run to pass.
            - A value of C(0.8) means 80% of test cases must pass.
        type: float
        default: 0.8
    report_format:
        description:
            - Format of the generated validation report.
        type: str
        choices:
            - json
            - html
            - pdf
        default: json
    config_id:
        description:
            - The ID of an existing validation configuration to update or delete.
        type: str
        required: false
    state:
        description:
            - Whether the configuration should exist or be removed.
        type: str
        choices:
            - present
            - absent
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
- name: Create a validation config for security testing
  stevefulme1.cisco_ai_defense.validation_config:
    name: "production-security-validation"
    categories:
      - prompt_injection
      - data_leakage
      - harmful_content
    pass_threshold: 0.9
    report_format: html
    state: present
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"

- name: Create a bias and compliance validation config
  stevefulme1.cisco_ai_defense.validation_config:
    name: "compliance-check"
    categories:
      - bias
      - compliance
    pass_threshold: 0.95
    state: present
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"

- name: Delete a validation configuration
  stevefulme1.cisco_ai_defense.validation_config:
    name: "deprecated-config"
    categories: []
    config_id: "cfg-12345"
    state: absent
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"
"""

RETURN = r"""
config:
    description: Details of the validation configuration.
    returned: success
    type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.cisco_ai_defense.plugins.module_utils.ai_defense import (
    AiDefenseClient,
)


def main():
    module_args = dict(
        name=dict(type="str", required=True),
        categories=dict(type="list", elements="str", required=True),
        pass_threshold=dict(type="float", default=0.8, no_log=False),
        report_format=dict(
            type="str",
            choices=["json", "html", "pdf"],
            default="json",
        ),
        config_id=dict(type="str"),
        state=dict(type="str", choices=["present", "absent"], default="present"),
        api_url=dict(type="str", required=True),
        api_key=dict(type="str", required=True, no_log=True),
        validate_certs=dict(type="bool", default=True),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    client = AiDefenseClient(module)
    state = module.params["state"]
    config_id = module.params.get("config_id")
    base_path = "/api/v1/validation/configs"

    # Fetch existing resource if an ID was provided
    existing = None
    if config_id:
        existing = client.get(f"{base_path}/{config_id}")

    if state == "absent":
        if existing is None:
            module.exit_json(changed=False)
        if module.check_mode:
            module.exit_json(changed=True)
        client.delete(f"{base_path}/{config_id}")
        module.exit_json(changed=True)

    payload = {
        "name": module.params["name"],
        "categories": module.params["categories"],
        "pass_threshold": module.params["pass_threshold"],
        "report_format": module.params["report_format"],
    }

    if existing is None:
        if module.check_mode:
            module.exit_json(changed=True)
        result = client.post(base_path, payload)
        module.exit_json(changed=True, config=result)

    # Update existing
    if module.check_mode:
        module.exit_json(changed=True)
    result = client.put(f"{base_path}/{config_id}", payload)
    module.exit_json(changed=True, config=result)


if __name__ == "__main__":
    main()
