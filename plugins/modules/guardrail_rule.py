# -*- coding: utf-8 -*-
# Copyright (c) 2024, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing individual guardrail rules in Cisco AI Defense."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: guardrail_rule
short_description: Manage individual guardrail rules in Cisco AI Defense
description:
    - Create, update, and delete individual rules within a Cisco AI Defense guardrail.
    - Rules define specific detection and enforcement behaviours such as prompt-injection
      blocking, PII detection, topic-drift prevention, content filtering, and data-leakage
      prevention.
    - Each rule belongs to a parent guardrail identified by I(guardrail_id).
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    guardrail_id:
        description:
            - The unique identifier of the parent guardrail this rule belongs to.
        type: str
        required: true
    name:
        description:
            - Human-readable name for the guardrail rule.
        type: str
        required: true
    rule_type:
        description:
            - The category of threat or policy violation this rule targets.
        type: str
        required: true
        choices:
            - prompt_injection
            - pii_detection
            - topic_drift
            - content_filter
            - data_leakage
    action:
        description:
            - The enforcement action to take when the rule triggers.
            - C(block) silently prevents the request or response from continuing.
            - C(alert) allows the request but generates an alert notification.
            - C(log) records the event without blocking or alerting.
        type: str
        choices:
            - block
            - alert
            - log
        default: block
    priority:
        description:
            - Numeric priority controlling evaluation order within the guardrail.
            - Lower values are evaluated first.
        type: int
        default: 100
    configuration:
        description:
            - Rule-specific configuration dictionary.
            - Contents vary by I(rule_type) and may include sensitivity thresholds,
              keyword lists, regex patterns, or model-specific parameters.
        type: dict
    rule_id:
        description:
            - The unique identifier of an existing rule.
            - Required when updating or deleting a specific rule.
        type: str
    state:
        description:
            - The desired state of the guardrail rule.
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
- name: Create a prompt-injection detection rule
  stevefulme1.cisco_ai_defense.guardrail_rule:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    guardrail_id: "grd-abc123"
    name: "Block prompt injection attacks"
    rule_type: prompt_injection
    action: block
    priority: 10
    configuration:
      sensitivity: high
      max_tokens_check: 2048
    state: present

- name: Add a PII detection rule with alert-only action
  stevefulme1.cisco_ai_defense.guardrail_rule:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    guardrail_id: "grd-abc123"
    name: "Detect PII in responses"
    rule_type: pii_detection
    action: alert
    priority: 20
    configuration:
      entity_types:
        - ssn
        - credit_card
        - email
    state: present

- name: Delete a guardrail rule
  stevefulme1.cisco_ai_defense.guardrail_rule:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    guardrail_id: "grd-abc123"
    rule_id: "rule-xyz789"
    name: "unused"
    rule_type: content_filter
    state: absent
"""

RETURN = r"""
rule:
    description: The guardrail rule object returned by the API.
    returned: on success when state is present
    type: dict
    contains:
        id:
            description: Unique rule identifier.
            type: str
            returned: always
        name:
            description: Rule name.
            type: str
            returned: always
        rule_type:
            description: Rule category.
            type: str
            returned: always
        action:
            description: Enforcement action.
            type: str
            returned: always
        priority:
            description: Evaluation priority.
            type: int
            returned: always
        configuration:
            description: Rule-specific settings.
            type: dict
            returned: when configured
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.cisco_ai_defense.plugins.module_utils.ai_defense import (
    AiDefenseClient,
)


def get_resource(client, guardrail_id, rule_id):
    """Retrieve existing rule."""
    if not rule_id:
        return None
    return client.get(f"/api/v1/guardrails/{guardrail_id}/rules/{rule_id}")


def create_resource(client, guardrail_id, params):
    """Create a new guardrail rule."""
    payload = {
        "name": params["name"],
        "rule_type": params["rule_type"],
        "action": params["action"],
        "priority": params["priority"],
    }
    if params.get("configuration"):
        payload["configuration"] = params["configuration"]
    return client.post(f"/api/v1/guardrails/{guardrail_id}/rules", payload)


def update_resource(client, guardrail_id, existing, params):
    """Update an existing guardrail rule."""
    resource_id = existing.get("id", "")
    payload = {
        "name": params["name"],
        "rule_type": params["rule_type"],
        "action": params["action"],
        "priority": params["priority"],
    }
    if params.get("configuration"):
        payload["configuration"] = params["configuration"]
    return client.put(f"/api/v1/guardrails/{guardrail_id}/rules/{resource_id}", payload)


def delete_resource(client, guardrail_id, existing):
    """Delete an existing guardrail rule."""
    resource_id = existing.get("id", "")
    client.delete(f"/api/v1/guardrails/{guardrail_id}/rules/{resource_id}")


def needs_update(params, existing):
    """Check if resource needs updating."""
    for attr in ("name", "rule_type", "action", "priority", "configuration"):
        desired = params.get(attr)
        if desired is None:
            continue
        if existing.get(attr) != desired:
            return True
    return False


def main():
    module_args = dict(
        guardrail_id=dict(type="str", required=True),
        name=dict(type="str", required=True),
        rule_type=dict(
            type="str",
            required=True,
            choices=["prompt_injection", "pii_detection", "topic_drift", "content_filter", "data_leakage"],
        ),
        action=dict(type="str", choices=["block", "alert", "log"], default="block"),
        priority=dict(type="int", default=100),
        configuration=dict(type="dict"),
        rule_id=dict(type="str"),
        state=dict(type="str", choices=["present", "absent"], default="present"),
        api_url=dict(type="str", required=True),
        api_key=dict(type="str", required=True, no_log=True),
        validate_certs=dict(type="bool", default=True),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    client = AiDefenseClient(module)
    guardrail_id = module.params["guardrail_id"]
    state = module.params["state"]

    existing = get_resource(client, guardrail_id, module.params.get("rule_id"))

    if state == "absent":
        if existing is None:
            module.exit_json(changed=False)
        if module.check_mode:
            module.exit_json(changed=True)
        delete_resource(client, guardrail_id, existing)
        module.exit_json(changed=True)

    if existing is None:
        if module.check_mode:
            module.exit_json(changed=True)
        resource = create_resource(client, guardrail_id, module.params)
        module.exit_json(changed=True, rule=resource)

    if needs_update(module.params, existing):
        if module.check_mode:
            module.exit_json(changed=True)
        resource = update_resource(client, guardrail_id, existing, module.params)
        module.exit_json(changed=True, rule=resource)

    module.exit_json(changed=False, rule=existing)


if __name__ == "__main__":
    main()
