# -*- coding: utf-8 -*-
# Copyright: (c) 2025, Steve Fulmer <sfulmer@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: cisco_aidefense_policy
short_description: Manage inspection policies in Cisco AI Defense
version_added: "0.1.0"
description:
  - Update or delete inspection policies in Cisco AI Defense.
  - Policies define which guardrail rules are applied during content inspection.
  - Policies are created automatically by the platform; this module manages
    their configuration and lifecycle.
  - Uses the Management API at /api/ai-defense/v1/policies.
author:
  - Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.cisco_ai_defense.aidefense
options:
  state:
    description:
      - Desired state of the policy.
    type: str
    default: present
    choices:
      - present
      - absent
  policy_id:
    description:
      - UUID of the policy to manage.
    type: str
    required: true
  name:
    description:
      - New name for the policy.
      - Only used when C(state=present).
    type: str
    required: false
  description:
    description:
      - New description for the policy.
    type: str
    required: false
  status:
    description:
      - Status of the policy.
    type: str
    required: false
    choices:
      - active
      - inactive
  connections_to_associate:
    description:
      - List of connection UUIDs to associate with this policy.
    type: list
    elements: str
    required: false
  connections_to_disassociate:
    description:
      - List of connection UUIDs to disassociate from this policy.
    type: list
    elements: str
    required: false
"""

EXAMPLES = r"""
- name: Update a policy name and status
  stevefulme1.cisco_ai_defense.cisco_aidefense_policy:
    api_key: "{{ aidefense_tenant_key }}"
    policy_id: "550e8400-e29b-41d4-a716-446655440000"
    name: "Strict Security Policy"
    status: active

- name: Associate connections with a policy
  stevefulme1.cisco_ai_defense.cisco_aidefense_policy:
    api_key: "{{ aidefense_tenant_key }}"
    policy_id: "550e8400-e29b-41d4-a716-446655440000"
    connections_to_associate:
      - "323e4567-e89b-12d3-a456-426614174333"

- name: Delete a policy
  stevefulme1.cisco_ai_defense.cisco_aidefense_policy:
    api_key: "{{ aidefense_tenant_key }}"
    policy_id: "550e8400-e29b-41d4-a716-446655440000"
    state: absent
"""

RETURN = r"""
policy:
  description: The policy object returned from the API after update.
  type: dict
  returned: when state is present
  contains:
    policy_id:
      description: UUID of the policy.
      type: str
    policy_name:
      description: Name of the policy.
      type: str
"""

from ansible.module_utils.basic import AnsibleModule


def main():
    argument_spec = dict(
        api_key=dict(type="str", required=True, no_log=True),
        region=dict(type="str", default="us", choices=["us", "eu", "apjc"]),
        validate_certs=dict(type="bool", default=True),
        timeout=dict(type="int", default=30),
        state=dict(type="str", default="present", choices=["present", "absent"]),
        policy_id=dict(type="str", required=True),
        name=dict(type="str", required=False, default=None),
        description=dict(type="str", required=False, default=None),
        status=dict(type="str", required=False, default=None, choices=["active", "inactive"]),
        connections_to_associate=dict(type="list", elements="str", required=False, default=None),
        connections_to_disassociate=dict(type="list", elements="str", required=False, default=None),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    from ansible_collections.stevefulme1.cisco_ai_defense.plugins.module_utils.aidefense_client import (
        ManagementClient,
        AiDefenseError,
    )

    state = module.params["state"]
    policy_id = module.params["policy_id"]

    try:
        client = ManagementClient(
            api_key=module.params["api_key"],
            region=module.params["region"],
            validate_certs=module.params["validate_certs"],
            timeout=module.params["timeout"],
        )

        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True, msg="Would delete policy.")
            client.delete_policy(policy_id)
            module.exit_json(changed=True, msg="Policy deleted.")

        # state == present
        changed = False

        # Update policy metadata if any fields provided
        update_fields = {}
        for field in ("name", "description", "status"):
            if module.params.get(field) is not None:
                update_fields[field] = module.params[field]

        if update_fields:
            if module.check_mode:
                module.exit_json(changed=True, msg="Would update policy.")
            client.update_policy(policy_id, **update_fields)
            changed = True

        # Update policy connections if specified
        associate = module.params.get("connections_to_associate")
        disassociate = module.params.get("connections_to_disassociate")
        if associate or disassociate:
            if module.check_mode:
                module.exit_json(changed=True, msg="Would update policy connections.")
            client.update_policy_connections(
                policy_id,
                associate=associate,
                disassociate=disassociate,
            )
            changed = True

        result = client.get_policy(policy_id)
        module.exit_json(changed=changed, policy=result)

    except AiDefenseError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
