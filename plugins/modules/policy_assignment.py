# -*- coding: utf-8 -*-
# Copyright (c) 2024, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for assigning policies to endpoints in Cisco AI Defense."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: policy_assignment
short_description: Assign policies to endpoints, models, or applications in Cisco AI Defense
description:
    - Create, update, and delete policy assignments that bind a policy to a specific
      target such as an endpoint, model, application, or group.
    - Assignments support policy inheritance so that child targets automatically
      receive the policies of their parent unless overridden.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    policy_id:
        description:
            - The unique identifier of the policy to assign.
        type: str
        required: true
    target_type:
        description:
            - The type of target the policy is being assigned to.
        type: str
        required: true
        choices:
            - endpoint
            - model
            - application
            - group
    target_id:
        description:
            - The unique identifier of the target receiving the policy assignment.
        type: str
        required: true
    inherit_parent:
        description:
            - Whether the target should also inherit policies assigned to its parent.
            - Set to C(false) to override parent policy assignments entirely.
        type: bool
        default: true
    assignment_id:
        description:
            - Unique identifier of an existing policy assignment.
            - Required when updating or deleting a specific assignment.
        type: str
    state:
        description:
            - The desired state of the policy assignment.
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
            - The API key for authentication.
        type: str
        required: true
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
- name: Assign a policy to a specific endpoint
  stevefulme1.cisco_ai_defense.policy_assignment:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    policy_id: "pol-abc123"
    target_type: endpoint
    target_id: "ep-chat-prod"
    inherit_parent: true
    state: present

- name: Assign a policy to a model without parent inheritance
  stevefulme1.cisco_ai_defense.policy_assignment:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    policy_id: "pol-pii-strict"
    target_type: model
    target_id: "mdl-gpt4-internal"
    inherit_parent: false
    state: present

- name: Remove a policy assignment
  stevefulme1.cisco_ai_defense.policy_assignment:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    policy_id: "pol-abc123"
    target_type: endpoint
    target_id: "ep-chat-prod"
    assignment_id: "asgn-xyz789"
    state: absent
"""

RETURN = r"""
assignment:
    description: The policy assignment object returned by the API.
    returned: on success when state is present
    type: dict
    contains:
        id:
            description: Unique assignment identifier.
            type: str
            returned: always
        policy_id:
            description: Assigned policy identifier.
            type: str
            returned: always
        target_type:
            description: Target type.
            type: str
            returned: always
        target_id:
            description: Target identifier.
            type: str
            returned: always
        inherit_parent:
            description: Whether parent inheritance is enabled.
            type: bool
            returned: always
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.cisco_ai_defense.plugins.module_utils.ai_defense import (
    AiDefenseClient,
)


def get_resource(client, resource_id):
    """Retrieve existing policy assignment."""
    if not resource_id:
        return None
    return client.get(f"/api/v1/policy_assignments/{resource_id}")


def create_resource(client, params):
    """Create a new policy assignment."""
    payload = {
        "policy_id": params["policy_id"],
        "target_type": params["target_type"],
        "target_id": params["target_id"],
        "inherit_parent": params["inherit_parent"],
    }
    return client.post("/api/v1/policy_assignments", payload)


def update_resource(client, existing, params):
    """Update an existing policy assignment."""
    resource_id = existing.get("id", "")
    payload = {
        "policy_id": params["policy_id"],
        "target_type": params["target_type"],
        "target_id": params["target_id"],
        "inherit_parent": params["inherit_parent"],
    }
    return client.put(f"/api/v1/policy_assignments/{resource_id}", payload)


def delete_resource(client, existing):
    """Delete an existing policy assignment."""
    resource_id = existing.get("id", "")
    client.delete(f"/api/v1/policy_assignments/{resource_id}")


def needs_update(params, existing):
    """Check if resource needs updating."""
    for attr in ("policy_id", "target_type", "target_id", "inherit_parent"):
        desired = params.get(attr)
        if desired is None:
            continue
        if existing.get(attr) != desired:
            return True
    return False


def main():
    module_args = dict(
        policy_id=dict(type="str", required=True),
        target_type=dict(type="str", required=True, choices=["endpoint", "model", "application", "group"]),
        target_id=dict(type="str", required=True),
        inherit_parent=dict(type="bool", default=True),
        assignment_id=dict(type="str"),
        state=dict(type="str", choices=["present", "absent"], default="present"),
        api_url=dict(type="str", required=True),
        api_key=dict(type="str", required=True, no_log=True),
        validate_certs=dict(type="bool", default=True),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    client = AiDefenseClient(module)
    state = module.params["state"]

    existing = get_resource(client, module.params.get("assignment_id"))

    if state == "absent":
        if existing is None:
            module.exit_json(changed=False)
        if module.check_mode:
            module.exit_json(changed=True)
        delete_resource(client, existing)
        module.exit_json(changed=True)

    if existing is None:
        if module.check_mode:
            module.exit_json(changed=True)
        resource = create_resource(client, module.params)
        module.exit_json(changed=True, assignment=resource)

    if needs_update(module.params, existing):
        if module.check_mode:
            module.exit_json(changed=True)
        resource = update_resource(client, existing, module.params)
        module.exit_json(changed=True, assignment=resource)

    module.exit_json(changed=False, assignment=existing)


if __name__ == "__main__":
    main()
