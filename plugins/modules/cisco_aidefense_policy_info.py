# -*- coding: utf-8 -*-
# Copyright: (c) 2025, Steve Fulmer <sfulmer@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: cisco_aidefense_policy_info
short_description: Query inspection policies from Cisco AI Defense
version_added: "0.1.0"
description:
  - Retrieve information about inspection policies in Cisco AI Defense.
  - Can fetch a single policy by ID or list all policies.
  - Uses the Management API at /api/ai-defense/v1/policies.
author:
  - Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.cisco_ai_defense.aidefense
options:
  policy_id:
    description:
      - UUID of a specific policy to retrieve.
      - When omitted, all policies are listed.
    type: str
    required: false
  limit:
    description:
      - Maximum number of policies to return when listing.
    type: int
    required: false
  offset:
    description:
      - Number of policies to skip for pagination.
    type: int
    required: false
"""

EXAMPLES = r"""
- name: List all policies
  stevefulme1.cisco_ai_defense.cisco_aidefense_policy_info:
    api_key: "{{ aidefense_tenant_key }}"
  register: policies

- name: Get a specific policy
  stevefulme1.cisco_ai_defense.cisco_aidefense_policy_info:
    api_key: "{{ aidefense_tenant_key }}"
    policy_id: "550e8400-e29b-41d4-a716-446655440000"
  register: policy
"""

RETURN = r"""
policy:
  description: Single policy details (when policy_id is provided).
  type: dict
  returned: when policy_id is specified
policies:
  description: List of policies (when listing).
  type: list
  elements: dict
  returned: when policy_id is not specified
"""

from ansible.module_utils.basic import AnsibleModule


def main():
    argument_spec = dict(
        api_key=dict(type="str", required=True, no_log=True),
        region=dict(type="str", default="us", choices=["us", "eu", "apjc"]),
        validate_certs=dict(type="bool", default=True),
        timeout=dict(type="int", default=30),
        policy_id=dict(type="str", required=False, default=None),
        limit=dict(type="int", required=False, default=None),
        offset=dict(type="int", required=False, default=None),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    from ansible_collections.stevefulme1.cisco_ai_defense.plugins.module_utils.aidefense_client import (
        ManagementClient,
        AiDefenseError,
    )

    try:
        client = ManagementClient(
            api_key=module.params["api_key"],
            region=module.params["region"],
            validate_certs=module.params["validate_certs"],
            timeout=module.params["timeout"],
        )

        policy_id = module.params.get("policy_id")
        if policy_id:
            result = client.get_policy(policy_id)
            module.exit_json(changed=False, policy=result)
        else:
            result = client.list_policies(
                limit=module.params.get("limit"),
                offset=module.params.get("offset"),
            )
            module.exit_json(changed=False, policies=result.get("policies", result))

    except AiDefenseError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
