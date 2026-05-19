# -*- coding: utf-8 -*-
# Copyright (c) 2024, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for configuring topic policies in Cisco AI Defense."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: topic_policy
short_description: Configure allowed and blocked topic policies in Cisco AI Defense
description:
    - Create, update, and delete topic policies that control which conversation
      topics an AI model is allowed or forbidden to discuss.
    - Topic policies use semantic scoring to determine whether a prompt or response
      falls within an allowed or blocked topic category.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    name:
        description:
            - Human-readable name for the topic policy.
        type: str
        required: true
    allowed_topics:
        description:
            - List of topic categories the AI model is permitted to discuss.
            - If both I(allowed_topics) and I(blocked_topics) are provided, blocked
              topics take precedence.
        type: list
        elements: str
    blocked_topics:
        description:
            - List of topic categories the AI model must not discuss.
        type: list
        elements: str
    scoring_threshold:
        description:
            - The minimum confidence score (0.0 to 1.0) required for a topic match
              to trigger enforcement.
            - Lower values are more aggressive; higher values reduce false positives.
        type: float
        default: 0.7
    enforcement_action:
        description:
            - The action to take when a blocked topic is detected.
            - C(block) prevents the request or response from proceeding.
            - C(warn) allows the interaction but returns a warning header.
            - C(log) records the event without interfering with the interaction.
        type: str
        choices:
            - block
            - warn
            - log
        default: block
    policy_id:
        description:
            - Unique identifier of an existing topic policy.
            - Required when updating or deleting a specific policy.
        type: str
    state:
        description:
            - The desired state of the topic policy.
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
- name: Create a topic policy that blocks harmful content categories
  stevefulme1.cisco_ai_defense.topic_policy:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    name: "Production safety policy"
    blocked_topics:
      - weapons
      - illegal_activities
      - self_harm
    allowed_topics:
      - technology
      - business
      - science
    scoring_threshold: 0.75
    enforcement_action: block
    state: present

- name: Create a logging-only topic policy for monitoring
  stevefulme1.cisco_ai_defense.topic_policy:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    name: "Topic monitoring policy"
    blocked_topics:
      - politics
      - religion
    scoring_threshold: 0.6
    enforcement_action: log
    state: present

- name: Delete a topic policy
  stevefulme1.cisco_ai_defense.topic_policy:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    name: "unused"
    policy_id: "tp-abc123"
    state: absent
"""

RETURN = r"""
topic_policy:
    description: The topic policy object returned by the API.
    returned: on success when state is present
    type: dict
    contains:
        id:
            description: Unique policy identifier.
            type: str
            returned: always
        name:
            description: Policy name.
            type: str
            returned: always
        allowed_topics:
            description: Permitted topic categories.
            type: list
            returned: when configured
        blocked_topics:
            description: Forbidden topic categories.
            type: list
            returned: when configured
        scoring_threshold:
            description: Confidence threshold for topic matching.
            type: float
            returned: always
        enforcement_action:
            description: Action taken on violation.
            type: str
            returned: always
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.cisco_ai_defense.plugins.module_utils.ai_defense import (
    AiDefenseClient,
)


def get_resource(client, resource_id):
    """Retrieve existing topic policy."""
    if not resource_id:
        return None
    return client.get(f"/api/v1/topic_policies/{resource_id}")


def create_resource(client, params):
    """Create a new topic policy."""
    payload = {
        "name": params["name"],
        "scoring_threshold": params["scoring_threshold"],
        "enforcement_action": params["enforcement_action"],
    }
    if params.get("allowed_topics"):
        payload["allowed_topics"] = params["allowed_topics"]
    if params.get("blocked_topics"):
        payload["blocked_topics"] = params["blocked_topics"]
    return client.post("/api/v1/topic_policies", payload)


def update_resource(client, existing, params):
    """Update an existing topic policy."""
    resource_id = existing.get("id", "")
    payload = {
        "name": params["name"],
        "scoring_threshold": params["scoring_threshold"],
        "enforcement_action": params["enforcement_action"],
    }
    if params.get("allowed_topics"):
        payload["allowed_topics"] = params["allowed_topics"]
    if params.get("blocked_topics"):
        payload["blocked_topics"] = params["blocked_topics"]
    return client.put(f"/api/v1/topic_policies/{resource_id}", payload)


def delete_resource(client, existing):
    """Delete an existing topic policy."""
    resource_id = existing.get("id", "")
    client.delete(f"/api/v1/topic_policies/{resource_id}")


def needs_update(params, existing):
    """Check if resource needs updating."""
    for attr in ("name", "scoring_threshold", "enforcement_action"):
        desired = params.get(attr)
        if desired is None:
            continue
        if existing.get(attr) != desired:
            return True
    for attr in ("allowed_topics", "blocked_topics"):
        desired = params.get(attr)
        if desired is None:
            continue
        current = existing.get(attr) or []
        if sorted(desired) != sorted(current):
            return True
    return False


def main():
    module_args = dict(
        name=dict(type="str", required=True),
        allowed_topics=dict(type="list", elements="str"),
        blocked_topics=dict(type="list", elements="str"),
        scoring_threshold=dict(type="float", default=0.7),
        enforcement_action=dict(type="str", choices=["block", "warn", "log"], default="block"),
        policy_id=dict(type="str"),
        state=dict(type="str", choices=["present", "absent"], default="present"),
        api_url=dict(type="str", required=True),
        api_key=dict(type="str", required=True, no_log=True),
        validate_certs=dict(type="bool", default=True),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    client = AiDefenseClient(module)
    state = module.params["state"]

    existing = get_resource(client, module.params.get("policy_id"))

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
        module.exit_json(changed=True, topic_policy=resource)

    if needs_update(module.params, existing):
        if module.check_mode:
            module.exit_json(changed=True)
        resource = update_resource(client, existing, module.params)
        module.exit_json(changed=True, topic_policy=resource)

    module.exit_json(changed=False, topic_policy=existing)


if __name__ == "__main__":
    main()
