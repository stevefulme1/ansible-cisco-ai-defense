# -*- coding: utf-8 -*-
# Copyright: (c) 2025, Steve Fulmer <sfulmer@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: cisco_aidefense_application_info
short_description: Query applications from Cisco AI Defense
version_added: "0.1.0"
description:
  - Retrieve information about applications registered in Cisco AI Defense.
  - Can fetch a single application by ID or list all applications.
  - Uses the Management API at /api/ai-defense/v1/applications.
author:
  - Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.cisco_ai_defense.aidefense
options:
  application_id:
    description:
      - UUID of a specific application to retrieve.
      - When omitted, all applications are listed.
    type: str
    required: false
  limit:
    description:
      - Maximum number of applications to return when listing.
    type: int
    required: false
  offset:
    description:
      - Number of applications to skip for pagination.
    type: int
    required: false
"""

EXAMPLES = r"""
- name: List all applications
  stevefulme1.cisco_ai_defense.cisco_aidefense_application_info:
    api_key: "{{ aidefense_tenant_key }}"
  register: apps

- name: Get a specific application
  stevefulme1.cisco_ai_defense.cisco_aidefense_application_info:
    api_key: "{{ aidefense_tenant_key }}"
    application_id: "123e4567-e89b-12d3-a456-426614174000"
  register: app
"""

RETURN = r"""
application:
  description: Single application details (when application_id is provided).
  type: dict
  returned: when application_id is specified
applications:
  description: List of applications (when listing).
  type: list
  elements: dict
  returned: when application_id is not specified
"""

from ansible.module_utils.basic import AnsibleModule


def main():
    argument_spec = dict(
        api_key=dict(type="str", required=True, no_log=True),
        region=dict(type="str", default="us", choices=["us", "eu", "apjc"]),
        validate_certs=dict(type="bool", default=True),
        timeout=dict(type="int", default=30),
        application_id=dict(type="str", required=False, default=None),
        limit=dict(type="int", required=False, default=None),
        offset=dict(type="int", required=False, default=None),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
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

        application_id = module.params.get("application_id")
        if application_id:
            result = client.get_application(application_id)
            module.exit_json(changed=False, application=result)
        else:
            result = client.list_applications(
                limit=module.params.get("limit"),
                offset=module.params.get("offset"),
            )
            module.exit_json(changed=False, applications=result.get("applications", result))

    except AiDefenseError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
