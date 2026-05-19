# -*- coding: utf-8 -*-
# Copyright (c) 2024, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for configuring PII detection and masking in Cisco AI Defense."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: pii_policy
short_description: Configure PII detection and masking policies in Cisco AI Defense
description:
    - Create, update, and delete PII (Personally Identifiable Information) detection
      and masking policies in Cisco AI Defense.
    - PII policies define which entity types to detect in AI model inputs and outputs
      and how to mask or redact them before they reach downstream consumers.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    name:
        description:
            - Human-readable name for the PII policy.
        type: str
        required: true
    entity_types:
        description:
            - List of PII entity types to detect.
            - At least one entity type must be specified.
        type: list
        elements: str
        required: true
        choices:
            - ssn
            - credit_card
            - email
            - phone
            - address
            - name
            - date_of_birth
            - passport
            - driver_license
            - custom
    masking_strategy:
        description:
            - The strategy used to mask detected PII.
            - C(redact) replaces PII with a placeholder such as C([REDACTED]).
            - C(mask) partially hides the value (e.g. C(***-**-1234)).
            - C(hash) replaces the value with a one-way hash.
            - C(tokenize) replaces PII with a reversible token for later de-tokenization.
        type: str
        choices:
            - redact
            - mask
            - hash
            - tokenize
        default: redact
    exceptions:
        description:
            - Optional list of patterns or entity values that should be exempted from
              detection even if they match a configured entity type.
        type: list
        elements: str
    policy_id:
        description:
            - Unique identifier of an existing PII policy.
            - Required when updating or deleting a specific policy.
        type: str
    state:
        description:
            - The desired state of the PII policy.
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
- name: Create a PII policy that redacts SSNs and credit cards
  stevefulme1.cisco_ai_defense.pii_policy:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    name: "Financial PII protection"
    entity_types:
      - ssn
      - credit_card
    masking_strategy: redact
    state: present

- name: Create a PII policy using tokenization for reversibility
  stevefulme1.cisco_ai_defense.pii_policy:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    name: "Customer support PII handling"
    entity_types:
      - email
      - phone
      - name
    masking_strategy: tokenize
    exceptions:
      - "support@example.com"
    state: present

- name: Delete a PII policy
  stevefulme1.cisco_ai_defense.pii_policy:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    name: "unused"
    entity_types:
      - email
    policy_id: "pii-abc123"
    state: absent
"""

RETURN = r"""
pii_policy:
    description: The PII policy object returned by the API.
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
        entity_types:
            description: PII entity types configured for detection.
            type: list
            returned: always
        masking_strategy:
            description: Masking strategy in use.
            type: str
            returned: always
        exceptions:
            description: Exempted patterns.
            type: list
            returned: when configured
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.cisco_ai_defense.plugins.module_utils.ai_defense import (
    AiDefenseClient,
)


def get_resource(client, resource_id):
    """Retrieve existing PII policy."""
    if not resource_id:
        return None
    return client.get(f"/api/v1/pii_policies/{resource_id}")


def create_resource(client, params):
    """Create a new PII policy."""
    payload = {
        "name": params["name"],
        "entity_types": params["entity_types"],
        "masking_strategy": params["masking_strategy"],
    }
    if params.get("exceptions"):
        payload["exceptions"] = params["exceptions"]
    return client.post("/api/v1/pii_policies", payload)


def update_resource(client, existing, params):
    """Update an existing PII policy."""
    resource_id = existing.get("id", "")
    payload = {
        "name": params["name"],
        "entity_types": params["entity_types"],
        "masking_strategy": params["masking_strategy"],
    }
    if params.get("exceptions"):
        payload["exceptions"] = params["exceptions"]
    return client.put(f"/api/v1/pii_policies/{resource_id}", payload)


def delete_resource(client, existing):
    """Delete an existing PII policy."""
    resource_id = existing.get("id", "")
    client.delete(f"/api/v1/pii_policies/{resource_id}")


def needs_update(params, existing):
    """Check if resource needs updating."""
    for attr in ("name", "entity_types", "masking_strategy", "exceptions"):
        desired = params.get(attr)
        if desired is None:
            continue
        current = existing.get(attr)
        if isinstance(desired, list) and isinstance(current, list):
            if sorted(desired) != sorted(current):
                return True
        elif current != desired:
            return True
    return False


def main():
    module_args = dict(
        name=dict(type="str", required=True),
        entity_types=dict(
            type="list",
            elements="str",
            required=True,
            choices=[
                "ssn", "credit_card", "email", "phone", "address",
                "name", "date_of_birth", "passport", "driver_license", "custom",
            ],
        ),
        masking_strategy=dict(
            type="str",
            choices=["redact", "mask", "hash", "tokenize"],
            default="redact",
        ),
        exceptions=dict(type="list", elements="str"),
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
        module.exit_json(changed=True, pii_policy=resource)

    if needs_update(module.params, existing):
        if module.check_mode:
            module.exit_json(changed=True)
        resource = update_resource(client, existing, module.params)
        module.exit_json(changed=True, pii_policy=resource)

    module.exit_json(changed=False, pii_policy=existing)


if __name__ == "__main__":
    main()
