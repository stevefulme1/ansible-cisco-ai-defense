# -*- coding: utf-8 -*-
# Copyright (c) 2024, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module to query discovered AI asset inventory in Cisco AI Defense."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: inventory_info
short_description: Query discovered AI asset inventory from Cisco AI Defense
description:
    - Retrieve the inventory of AI assets discovered by Cisco AI Defense.
    - Filter results by asset type, cloud provider, or risk level to focus
      on the assets most relevant to your security posture.
    - Returns details such as asset name, type, location, and associated risk.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    asset_type:
        description:
            - Filter assets by their type.
            - C(model) returns AI/ML model deployments.
            - C(agent) returns autonomous AI agent instances.
            - C(endpoint) returns API endpoints serving AI workloads.
            - C(mcp_server) returns Model Context Protocol servers.
        type: str
        choices:
            - model
            - agent
            - endpoint
            - mcp_server
        required: false
    cloud_provider:
        description:
            - Filter assets deployed on a specific cloud provider such as C(aws),
              C(azure), or C(gcp).
        type: str
        required: false
    risk_level:
        description:
            - Filter assets by their calculated risk level.
        type: str
        choices:
            - critical
            - high
            - medium
            - low
        required: false
    limit:
        description:
            - Maximum number of assets to return.
        type: int
        default: 100
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
- name: List all discovered AI assets
  stevefulme1.cisco_ai_defense.inventory_info:
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"
  register: all_assets

- name: Retrieve only high-risk model deployments
  stevefulme1.cisco_ai_defense.inventory_info:
    asset_type: model
    risk_level: high
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"

- name: Retrieve MCP servers running on AWS
  stevefulme1.cisco_ai_defense.inventory_info:
    asset_type: mcp_server
    cloud_provider: aws
    limit: 50
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"
"""

RETURN = r"""
assets:
    description: List of discovered AI assets matching the query filters.
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
        asset_type=dict(
            type="str",
            choices=["model", "agent", "endpoint", "mcp_server"],
        ),
        cloud_provider=dict(type="str"),
        risk_level=dict(
            type="str",
            choices=["critical", "high", "medium", "low"],
        ),
        limit=dict(type="int", default=100),
        api_url=dict(type="str", required=True),
        api_key=dict(type="str", required=True, no_log=True),
        validate_certs=dict(type="bool", default=True),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    client = AiDefenseClient(module)

    params = {"limit": module.params["limit"]}
    if module.params.get("asset_type"):
        params["asset_type"] = module.params["asset_type"]
    if module.params.get("cloud_provider"):
        params["cloud_provider"] = module.params["cloud_provider"]
    if module.params.get("risk_level"):
        params["risk_level"] = module.params["risk_level"]

    result = client.get("/api/v1/inventory/assets", params=params)
    module.exit_json(changed=False, assets=result)


if __name__ == "__main__":
    main()
