# -*- coding: utf-8 -*-
# Copyright (c) 2024, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for configuring Splunk telemetry export in Cisco AI Defense."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: splunk_integration
short_description: Configure Splunk telemetry export for Cisco AI Defense
description:
    - Create, update, and delete Splunk HTTP Event Collector (HEC) integrations
      for streaming Cisco AI Defense telemetry events to Splunk.
    - Events are forwarded in near-real-time and include threat detections,
      policy violations, validation results, and audit trail entries.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    name:
        description:
            - Human-readable name for the Splunk integration.
        type: str
        required: true
    splunk_url:
        description:
            - The Splunk HEC endpoint URL, typically
              C(https://splunk.example.com:8088/services/collector).
        type: str
        required: true
    splunk_token:
        description:
            - The Splunk HEC authentication token.
        type: str
        required: true
        no_log: true
    event_types:
        description:
            - List of event categories to forward to Splunk.
        type: list
        elements: str
        choices:
            - threats
            - policy_violations
            - validation_results
            - audit_events
    severity_filter:
        description:
            - Minimum severity level for events forwarded to Splunk.
            - C(all) forwards every event regardless of severity.
        type: str
        choices:
            - all
            - critical
            - high
            - medium
        default: all
    index_name:
        description:
            - The Splunk index where events should be stored.
        type: str
        default: "cisco_ai_defense"
    integration_id:
        description:
            - Unique identifier of an existing Splunk integration.
            - Required when updating or deleting a specific integration.
        type: str
    state:
        description:
            - The desired state of the Splunk integration.
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
- name: Create a Splunk integration for threat events
  stevefulme1.cisco_ai_defense.splunk_integration:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    name: "Production Splunk feed"
    splunk_url: "https://splunk.example.com:8088/services/collector"
    splunk_token: "{{ vault_splunk_hec_token }}"
    event_types:
      - threats
      - policy_violations
    severity_filter: high
    index_name: "ai_security"
    state: present

- name: Create a comprehensive audit integration
  stevefulme1.cisco_ai_defense.splunk_integration:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    name: "Full audit trail"
    splunk_url: "https://splunk.example.com:8088/services/collector"
    splunk_token: "{{ vault_splunk_hec_token }}"
    event_types:
      - threats
      - policy_violations
      - validation_results
      - audit_events
    severity_filter: all
    state: present

- name: Remove a Splunk integration
  stevefulme1.cisco_ai_defense.splunk_integration:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    name: "unused"
    splunk_url: "https://unused"
    splunk_token: "unused"
    integration_id: "int-abc123"
    state: absent
"""

RETURN = r"""
integration:
    description: The Splunk integration object returned by the API.
    returned: on success when state is present
    type: dict
    contains:
        id:
            description: Unique integration identifier.
            type: str
            returned: always
        name:
            description: Integration name.
            type: str
            returned: always
        splunk_url:
            description: Splunk HEC endpoint URL.
            type: str
            returned: always
        event_types:
            description: Event categories being forwarded.
            type: list
            returned: always
        severity_filter:
            description: Minimum severity filter.
            type: str
            returned: always
        index_name:
            description: Target Splunk index.
            type: str
            returned: always
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.cisco_ai_defense.plugins.module_utils.ai_defense import (
    AiDefenseClient,
)


def get_resource(client, resource_id):
    """Retrieve existing Splunk integration."""
    if not resource_id:
        return None
    return client.get(f"/api/v1/integrations/splunk/{resource_id}")


def create_resource(client, params):
    """Create a new Splunk integration."""
    payload = {
        "name": params["name"],
        "splunk_url": params["splunk_url"],
        "splunk_token": params["splunk_token"],
        "severity_filter": params["severity_filter"],
        "index_name": params["index_name"],
    }
    if params.get("event_types"):
        payload["event_types"] = params["event_types"]
    return client.post("/api/v1/integrations/splunk", payload)


def update_resource(client, existing, params):
    """Update an existing Splunk integration."""
    resource_id = existing.get("id", "")
    payload = {
        "name": params["name"],
        "splunk_url": params["splunk_url"],
        "splunk_token": params["splunk_token"],
        "severity_filter": params["severity_filter"],
        "index_name": params["index_name"],
    }
    if params.get("event_types"):
        payload["event_types"] = params["event_types"]
    return client.put(f"/api/v1/integrations/splunk/{resource_id}", payload)


def delete_resource(client, existing):
    """Delete an existing Splunk integration."""
    resource_id = existing.get("id", "")
    client.delete(f"/api/v1/integrations/splunk/{resource_id}")


def needs_update(params, existing):
    """Check if resource needs updating."""
    for attr in ("name", "splunk_url", "severity_filter", "index_name"):
        desired = params.get(attr)
        if desired is None:
            continue
        if existing.get(attr) != desired:
            return True
    # Always treat splunk_token as potentially changed (no_log prevents comparison)
    if params.get("splunk_token"):
        return True
    desired_types = params.get("event_types")
    if desired_types:
        current_types = existing.get("event_types") or []
        if sorted(desired_types) != sorted(current_types):
            return True
    return False


def main():
    module_args = dict(
        name=dict(type="str", required=True),
        splunk_url=dict(type="str", required=True),
        splunk_token=dict(type="str", required=True, no_log=True),
        event_types=dict(
            type="list",
            elements="str",
            choices=["threats", "policy_violations", "validation_results", "audit_events"],
        ),
        severity_filter=dict(type="str", choices=["all", "critical", "high", "medium"], default="all"),
        index_name=dict(type="str", default="cisco_ai_defense"),
        integration_id=dict(type="str"),
        state=dict(type="str", choices=["present", "absent"], default="present"),
        api_url=dict(type="str", required=True),
        api_key=dict(type="str", required=True, no_log=True),
        validate_certs=dict(type="bool", default=True),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    client = AiDefenseClient(module)
    state = module.params["state"]

    existing = get_resource(client, module.params.get("integration_id"))

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
        module.exit_json(changed=True, integration=resource)

    if needs_update(module.params, existing):
        if module.check_mode:
            module.exit_json(changed=True)
        resource = update_resource(client, existing, module.params)
        module.exit_json(changed=True, integration=resource)

    module.exit_json(changed=False, integration=existing)


if __name__ == "__main__":
    main()
