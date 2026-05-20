# -*- coding: utf-8 -*-
# Copyright: (c) 2025, Steve Fulmer <sfulmer@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: cisco_aidefense_inspect_info
short_description: Query inspection events from Cisco AI Defense
version_added: "0.1.0"
description:
  - Retrieve inspection event details from the Cisco AI Defense Management API.
  - Can fetch a single event by ID or list recent events.
  - Uses the Management API events endpoints.
author:
  - Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.cisco_ai_defense.aidefense
options:
  event_id:
    description:
      - The ID of a specific inspection event to retrieve.
      - Mutually exclusive with C(limit) and C(offset).
    type: str
    required: false
  limit:
    description:
      - Maximum number of events to return when listing.
    type: int
    required: false
  offset:
    description:
      - Number of events to skip for pagination.
    type: int
    required: false
"""

EXAMPLES = r"""
- name: Get a specific inspection event
  stevefulme1.cisco_ai_defense.cisco_aidefense_inspect_info:
    api_key: "{{ aidefense_tenant_key }}"
    event_id: "evt-12345678-abcd-1234-efgh-123456789012"
  register: event

- name: List recent inspection events
  stevefulme1.cisco_ai_defense.cisco_aidefense_inspect_info:
    api_key: "{{ aidefense_tenant_key }}"
    limit: 20
  register: events
"""

RETURN = r"""
event:
  description: Single inspection event details (when event_id is provided).
  type: dict
  returned: when event_id is specified
events:
  description: List of inspection events (when listing).
  type: list
  elements: dict
  returned: when event_id is not specified
"""

from ansible.module_utils.basic import AnsibleModule


def main():
    argument_spec = dict(
        api_key=dict(type="str", required=True, no_log=True),
        region=dict(type="str", default="us", choices=["us", "eu", "apjc"]),
        validate_certs=dict(type="bool", default=True),
        timeout=dict(type="int", default=30),
        event_id=dict(type="str", required=False, default=None),
        limit=dict(type="int", required=False, default=None),
        offset=dict(type="int", required=False, default=None),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[
            ("event_id", "limit"),
            ("event_id", "offset"),
        ],
        supports_check_mode=True,
    )

    from ansible_collections.stevefulme1.cisco_ai_defense.plugins.module_utils.aidefense_client import (
        ManagementClient,
        AiDefenseError,
    )

    try:
        client = ManagementClient(
            api_key=module.params["api_key"],
            region=module.params["region"],
            validate_certs=module.params["validate_certs"],
            timeout=module.params["timeout"],
        )

        event_id = module.params.get("event_id")
        if event_id:
            result = client._request("GET", "events/{0}".format(event_id))
            module.exit_json(changed=False, event=result)
        else:
            params = {}
            if module.params.get("limit") is not None:
                params["limit"] = module.params["limit"]
            if module.params.get("offset") is not None:
                params["offset"] = module.params["offset"]
            result = client._request("GET", "events", params=params)
            module.exit_json(changed=False, events=result.get("events", []))

    except AiDefenseError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
