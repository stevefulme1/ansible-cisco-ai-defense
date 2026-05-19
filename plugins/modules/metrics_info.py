# -*- coding: utf-8 -*-
# Copyright (c) 2024, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for retrieving protection metrics from Cisco AI Defense."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: metrics_info
short_description: Retrieve protection metrics from Cisco AI Defense
description:
    - Query protection and observability metrics from Cisco AI Defense.
    - Supports filtering by metric type, time range, and grouping dimension.
    - This is a read-only module that never modifies state.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    metric_type:
        description:
            - The category of metrics to retrieve.
            - When omitted, an aggregate summary of all metric types is returned.
        type: str
        choices:
            - blocked_requests
            - pii_detected
            - validation_scores
            - threat_events
    time_range:
        description:
            - The time window over which to aggregate metrics.
        type: str
        choices:
            - 1h
            - 24h
            - 7d
            - 30d
            - 90d
        default: "24h"
    group_by:
        description:
            - Optionally group results by a specific dimension.
        type: str
        choices:
            - endpoint
            - policy
            - category
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
- name: Retrieve all metrics for the last 24 hours
  stevefulme1.cisco_ai_defense.metrics_info:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
  register: all_metrics

- name: Get blocked-request metrics for the last 7 days grouped by endpoint
  stevefulme1.cisco_ai_defense.metrics_info:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    metric_type: blocked_requests
    time_range: "7d"
    group_by: endpoint
  register: blocked_metrics

- name: Get PII detection events for the last hour
  stevefulme1.cisco_ai_defense.metrics_info:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    metric_type: pii_detected
    time_range: "1h"
  register: pii_metrics

- name: Display threat events grouped by policy over 90 days
  stevefulme1.cisco_ai_defense.metrics_info:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    metric_type: threat_events
    time_range: "90d"
    group_by: policy
  register: threat_metrics
"""

RETURN = r"""
metrics:
    description: The metrics data returned by the API.
    returned: always
    type: dict
    contains:
        metric_type:
            description: The type of metrics returned.
            type: str
            returned: always
        time_range:
            description: The time range queried.
            type: str
            returned: always
        data_points:
            description: List of metric data points.
            type: list
            elements: dict
            returned: always
        group_by:
            description: The grouping dimension if specified.
            type: str
            returned: when group_by is specified
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.cisco_ai_defense.plugins.module_utils.ai_defense import (
    AiDefenseClient,
)


def main():
    module_args = dict(
        metric_type=dict(
            type="str",
            choices=["blocked_requests", "pii_detected", "validation_scores", "threat_events"],
        ),
        time_range=dict(type="str", choices=["1h", "24h", "7d", "30d", "90d"], default="24h"),
        group_by=dict(type="str", choices=["endpoint", "policy", "category"]),
        api_url=dict(type="str", required=True),
        api_key=dict(type="str", required=True, no_log=True),
        validate_certs=dict(type="bool", default=True),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    client = AiDefenseClient(module)

    params = {"time_range": module.params["time_range"]}
    if module.params.get("metric_type"):
        params["metric_type"] = module.params["metric_type"]
    if module.params.get("group_by"):
        params["group_by"] = module.params["group_by"]

    result = client.get("/api/v1/metrics", params=params)

    module.exit_json(changed=False, metrics=result)


if __name__ == "__main__":
    main()
