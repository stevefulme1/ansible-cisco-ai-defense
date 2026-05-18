# -*- coding: utf-8 -*-
# Copyright (c) 2024, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for managing Cisco AI Defense guardrail."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: guardrail
short_description: Manage guardrails in Cisco AI Defense
description:
    - Manage guardrails in Cisco AI Defense via the Cisco AI Defense REST API.
version_added: "1.0.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    name:
        description:
            - The name parameter.
        type: str
        required: true
    guardrail_type:
        description:
            - The guardrail type parameter.
        type: str
        required: true
    configuration:
        description:
            - The configuration parameter.
        type: str
        required: true
    guardrail_id:
        description:
            - The guardrail id parameter.
        type: str
        required: false
    state:
        description:
            - The desired state of the resource.
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
- name: Create guardrail
  stevefulme1.cisco_ai_defense.guardrail:
    name: "example-value"
    guardrail_type: "example-value"
    configuration: "example-value"
    state: present

- name: Delete guardrail
  stevefulme1.cisco_ai_defense.guardrail:
    guardrail_id: "example-value"
    state: absent
"""

RETURN = r"""
guardrail:
    description: Details of the guardrail.
    returned: On success.
    type: dict
"""

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

from ansible.module_utils.basic import AnsibleModule


def get_resource(module, api_url, headers):
    """Retrieve existing resource."""
    resource_id = module.params.get("guardrail_id")
    if not resource_id:
        return None
    try:
        url = f"{api_url}/api/v1/guardrail/{resource_id}"
        response = requests.get(
            url, headers=headers,
            verify=module.params["validate_certs"],
            timeout=30,
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def create_resource(module, api_url, headers):
    """Create a new resource."""
    payload = {}
    if module.params.get("name"):
        payload["name"] = module.params["name"]
    if module.params.get("guardrail_type"):
        payload["guardrail_type"] = module.params["guardrail_type"]
    if module.params.get("configuration"):
        payload["configuration"] = module.params["configuration"]
    response = requests.post(
        f"{api_url}/api/v1/guardrail",
        headers=headers, json=payload,
        verify=module.params["validate_certs"],
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def update_resource(module, api_url, headers, existing):
    """Update an existing resource."""
    resource_id = existing.get("id", "")
    payload = {}
    if module.params.get("name"):
        payload["name"] = module.params["name"]
    if module.params.get("guardrail_type"):
        payload["guardrail_type"] = module.params["guardrail_type"]
    if module.params.get("configuration"):
        payload["configuration"] = module.params["configuration"]
    response = requests.put(
        f"{api_url}/api/v1/guardrail/{resource_id}",
        headers=headers, json=payload,
        verify=module.params["validate_certs"],
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def delete_resource(module, api_url, headers, existing):
    """Delete an existing resource."""
    resource_id = existing.get("id", "")
    response = requests.delete(
        f"{api_url}/api/v1/guardrail/{resource_id}",
        headers=headers,
        verify=module.params["validate_certs"],
        timeout=30,
    )
    response.raise_for_status()


def needs_update(params, existing):
    """Check if resource needs updating."""
    updatable = ['name', 'guardrail_type', 'configuration']
    for attr in updatable:
        desired = params.get(attr)
        if desired is None:
            continue
        current = existing.get(attr)
        if current != desired:
            return True
    return False


def main():
    module_args = dict(
        name=dict(type="str", required=True),
        guardrail_type=dict(type="str", required=True),
        configuration=dict(type="str", required=True),
        guardrail_id=dict(type="str"),
        state=dict(type="str", choices=["present", "absent"], default="present"),
        api_url=dict(type="str", required=True),
        api_key=dict(type="str", required=True, no_log=True),
        validate_certs=dict(type="bool", default=True),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    api_url = module.params["api_url"].rstrip("/")
    headers = {
        "Authorization": f"Bearer {module.params['api_key']}",
        "Content-Type": "application/json",
    }
    state = module.params["state"]

    try:
        existing = get_resource(module, api_url, headers)
    except requests.RequestException as e:
        module.fail_json(msg=f"API request failed: {e}")

    if state == "absent":
        if existing is None:
            module.exit_json(changed=False)
        if module.check_mode:
            module.exit_json(changed=True)
        try:
            delete_resource(module, api_url, headers, existing)
        except requests.RequestException as e:
            module.fail_json(msg=f"Failed to delete resource: {e}")
        module.exit_json(changed=True)

    if existing is None:
        if module.check_mode:
            module.exit_json(changed=True)
        try:
            resource = create_resource(module, api_url, headers)
        except requests.RequestException as e:
            module.fail_json(msg=f"Failed to create resource: {e}")
        module.exit_json(changed=True, guardrail=resource)

    if needs_update(module.params, existing):
        if module.check_mode:
            module.exit_json(changed=True)
        try:
            resource = update_resource(module, api_url, headers, existing)
        except requests.RequestException as e:
            module.fail_json(msg=f"Failed to update resource: {e}")
        module.exit_json(changed=True, guardrail=resource)

    module.exit_json(changed=False, guardrail=existing)


if __name__ == "__main__":
    main()
