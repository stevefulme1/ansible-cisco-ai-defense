# -*- coding: utf-8 -*-
# Copyright (c) 2024, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for configuring rate limiting in Cisco AI Defense."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: rate_limit
short_description: Configure rate limiting in Cisco AI Defense
description:
    - Create, update, and delete rate-limiting configurations for Cisco AI Defense
      protected endpoints.
    - Rate limits control how many requests a given scope (user, application, or endpoint)
      may make within a rolling one-minute window, with optional burst allowances.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    name:
        description:
            - Human-readable name for the rate-limiting configuration.
        type: str
        required: true
    endpoint_pattern:
        description:
            - URL pattern that identifies which endpoints this rate limit applies to.
            - Supports glob-style wildcards such as C(/api/v1/chat/*).
        type: str
        required: true
    requests_per_minute:
        description:
            - Maximum number of requests allowed per minute within the configured scope.
        type: int
        required: true
    burst_limit:
        description:
            - Maximum number of requests allowed in a short burst before throttling kicks in.
            - When omitted the API applies its own default burst behaviour.
        type: int
    scope:
        description:
            - The scope at which the rate limit is enforced.
            - C(per_user) limits each authenticated user independently.
            - C(per_application) limits all traffic from a single application.
            - C(per_endpoint) applies a shared limit across all callers.
        type: str
        choices:
            - per_user
            - per_application
            - per_endpoint
        default: per_endpoint
    rate_limit_id:
        description:
            - Unique identifier of an existing rate-limit configuration.
            - Required when updating or deleting a specific rate limit.
        type: str
    state:
        description:
            - The desired state of the rate-limit configuration.
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
- name: Create a per-user rate limit for the chat endpoint
  stevefulme1.cisco_ai_defense.rate_limit:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    name: "Chat endpoint user limit"
    endpoint_pattern: "/api/v1/chat/*"
    requests_per_minute: 60
    burst_limit: 10
    scope: per_user
    state: present

- name: Create a global per-endpoint rate limit
  stevefulme1.cisco_ai_defense.rate_limit:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    name: "Global completions limit"
    endpoint_pattern: "/api/v1/completions"
    requests_per_minute: 1000
    scope: per_endpoint
    state: present

- name: Remove a rate limit
  stevefulme1.cisco_ai_defense.rate_limit:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    name: "unused"
    endpoint_pattern: "/unused"
    requests_per_minute: 1
    rate_limit_id: "rl-abc123"
    state: absent
"""

RETURN = r"""
rate_limit:
    description: The rate-limit configuration object returned by the API.
    returned: on success when state is present
    type: dict
    contains:
        id:
            description: Unique identifier.
            type: str
            returned: always
        name:
            description: Rate-limit name.
            type: str
            returned: always
        endpoint_pattern:
            description: URL pattern.
            type: str
            returned: always
        requests_per_minute:
            description: Per-minute request cap.
            type: int
            returned: always
        burst_limit:
            description: Burst allowance.
            type: int
            returned: when configured
        scope:
            description: Enforcement scope.
            type: str
            returned: always
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.cisco_ai_defense.plugins.module_utils.ai_defense import (
    AiDefenseClient,
)


def get_resource(client, resource_id):
    """Retrieve existing rate limit."""
    if not resource_id:
        return None
    return client.get(f"/api/v1/rate_limits/{resource_id}")


def create_resource(client, params):
    """Create a new rate limit."""
    payload = {
        "name": params["name"],
        "endpoint_pattern": params["endpoint_pattern"],
        "requests_per_minute": params["requests_per_minute"],
        "scope": params["scope"],
    }
    if params.get("burst_limit") is not None:
        payload["burst_limit"] = params["burst_limit"]
    return client.post("/api/v1/rate_limits", payload)


def update_resource(client, existing, params):
    """Update an existing rate limit."""
    resource_id = existing.get("id", "")
    payload = {
        "name": params["name"],
        "endpoint_pattern": params["endpoint_pattern"],
        "requests_per_minute": params["requests_per_minute"],
        "scope": params["scope"],
    }
    if params.get("burst_limit") is not None:
        payload["burst_limit"] = params["burst_limit"]
    return client.put(f"/api/v1/rate_limits/{resource_id}", payload)


def delete_resource(client, existing):
    """Delete an existing rate limit."""
    resource_id = existing.get("id", "")
    client.delete(f"/api/v1/rate_limits/{resource_id}")


def needs_update(params, existing):
    """Check if resource needs updating."""
    for attr in ("name", "endpoint_pattern", "requests_per_minute", "burst_limit", "scope"):
        desired = params.get(attr)
        if desired is None:
            continue
        if existing.get(attr) != desired:
            return True
    return False


def main():
    module_args = dict(
        name=dict(type="str", required=True),
        endpoint_pattern=dict(type="str", required=True),
        requests_per_minute=dict(type="int", required=True),
        burst_limit=dict(type="int"),
        scope=dict(type="str", choices=["per_user", "per_application", "per_endpoint"], default="per_endpoint"),
        rate_limit_id=dict(type="str"),
        state=dict(type="str", choices=["present", "absent"], default="present"),
        api_url=dict(type="str", required=True),
        api_key=dict(type="str", required=True, no_log=True),
        validate_certs=dict(type="bool", default=True),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    client = AiDefenseClient(module)
    state = module.params["state"]

    existing = get_resource(client, module.params.get("rate_limit_id"))

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
        module.exit_json(changed=True, rate_limit=resource)

    if needs_update(module.params, existing):
        if module.check_mode:
            module.exit_json(changed=True)
        resource = update_resource(client, existing, module.params)
        module.exit_json(changed=True, rate_limit=resource)

    module.exit_json(changed=False, rate_limit=existing)


if __name__ == "__main__":
    main()
