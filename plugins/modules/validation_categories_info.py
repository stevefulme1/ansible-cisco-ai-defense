# -*- coding: utf-8 -*-
# Copyright (c) 2024, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module to list available validation categories in Cisco AI Defense."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: validation_categories_info
short_description: List available validation categories from Cisco AI Defense
description:
    - Retrieve the list of validation categories available in Cisco AI Defense.
    - Categories represent types of adversarial tests such as prompt injection,
      data leakage, bias detection, and compliance checks.
    - Use this module to discover available categories before configuring
      validation runs or schedules.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    category_type:
        description:
            - Filter categories by their top-level type.
            - C(security) covers prompt injection, jailbreaks, and similar attacks.
            - C(safety) covers harmful content and toxicity checks.
            - C(bias) covers fairness and bias detection tests.
            - C(compliance) covers regulatory and policy compliance checks.
        type: str
        choices:
            - security
            - safety
            - bias
            - compliance
        required: false
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
- name: List all available validation categories
  stevefulme1.cisco_ai_defense.validation_categories_info:
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"
  register: all_categories

- name: List only security-related validation categories
  stevefulme1.cisco_ai_defense.validation_categories_info:
    category_type: security
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"

- name: List bias detection categories
  stevefulme1.cisco_ai_defense.validation_categories_info:
    category_type: bias
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"
"""

RETURN = r"""
categories:
    description: List of available validation categories.
    returned: success
    type: list
    elements: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.cisco_ai_defense.plugins.module_utils.ai_defense import (
    AiDefenseClient,
)


def main():
    module_args = dict(
        category_type=dict(
            type="str",
            choices=["security", "safety", "bias", "compliance"],
        ),
        api_url=dict(type="str", required=True),
        api_key=dict(type="str", required=True, no_log=True),
        validate_certs=dict(type="bool", default=True),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    client = AiDefenseClient(module)

    params = {}
    if module.params.get("category_type"):
        params["category_type"] = module.params["category_type"]

    result = client.get("/api/v1/validation/categories", params=params or None)
    categories = result if isinstance(result, list) else result.get("categories", [])
    module.exit_json(changed=False, categories=categories)


if __name__ == "__main__":
    main()
