# -*- coding: utf-8 -*-
# Copyright: (c) 2025, Steve Fulmer <sfulmer@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: cisco_aidefense_connection
short_description: Manage API connections in Cisco AI Defense
version_added: "0.1.0"
description:
  - Create or delete API connections in Cisco AI Defense.
  - Connections link applications to the AI Defense inspection service
    and provide API keys for runtime inspection.
  - Uses the Management API at /api/ai-defense/v1/connections.
author:
  - Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.cisco_ai_defense.aidefense
options:
  state:
    description:
      - Desired state of the connection.
    type: str
    default: present
    choices:
      - present
      - absent
  connection_id:
    description:
      - UUID of an existing connection.
      - Required when C(state=absent).
    type: str
    required: false
  application_id:
    description:
      - UUID of the application this connection belongs to.
      - Required when C(state=present) and creating a new connection.
    type: str
    required: false
  connection_name:
    description:
      - Name for the connection.
      - Required when C(state=present) and creating a new connection.
    type: str
    required: false
  connection_type:
    description:
      - Type of connection.
    type: str
    required: false
    default: API
    choices:
      - API
      - Gateway
"""

EXAMPLES = r"""
- name: Create a connection
  stevefulme1.cisco_ai_defense.cisco_aidefense_connection:
    api_key: "{{ aidefense_tenant_key }}"
    application_id: "123e4567-e89b-12d3-a456-426614174000"
    connection_name: "Production API Connection"
    connection_type: API
  register: conn

- name: Delete a connection
  stevefulme1.cisco_ai_defense.cisco_aidefense_connection:
    api_key: "{{ aidefense_tenant_key }}"
    connection_id: "{{ conn.connection.connection_id }}"
    state: absent
"""

RETURN = r"""
connection:
  description: The connection object returned from the API.
  type: dict
  returned: when state is present
  contains:
    connection_id:
      description: UUID of the connection.
      type: str
    connection_name:
      description: Name of the connection.
      type: str
    connection_type:
      description: Type of connection.
      type: str
"""

from ansible.module_utils.basic import AnsibleModule


def main():
    argument_spec = dict(
        api_key=dict(type="str", required=True, no_log=True),
        region=dict(type="str", default="us", choices=["us", "eu", "apjc"]),
        validate_certs=dict(type="bool", default=True),
        timeout=dict(type="int", default=30),
        state=dict(type="str", default="present", choices=["present", "absent"]),
        connection_id=dict(type="str", required=False, default=None),
        application_id=dict(type="str", required=False, default=None),
        connection_name=dict(type="str", required=False, default=None),
        connection_type=dict(type="str", required=False, default="API", choices=["API", "Gateway"]),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[
            ("state", "absent", ("connection_id",)),
        ],
        supports_check_mode=True,
    )

    from ansible_collections.stevefulme1.cisco_ai_defense.plugins.module_utils.aidefense_client import (
        ManagementClient,
        AiDefenseError,
    )

    state = module.params["state"]
    connection_id = module.params.get("connection_id")

    try:
        client = ManagementClient(
            api_key=module.params["api_key"],
            region=module.params["region"],
            validate_certs=module.params["validate_certs"],
            timeout=module.params["timeout"],
        )

        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True, msg="Would delete connection.")
            client.delete_connection(connection_id)
            module.exit_json(changed=True, msg="Connection deleted.")

        # state == present - create new connection
        if not module.params.get("application_id"):
            module.fail_json(msg="application_id is required when creating a new connection.")
        if not module.params.get("connection_name"):
            module.fail_json(msg="connection_name is required when creating a new connection.")

        if module.check_mode:
            module.exit_json(changed=True, msg="Would create connection.")

        result = client.create_connection(
            application_id=module.params["application_id"],
            connection_name=module.params["connection_name"],
            connection_type=module.params.get("connection_type", "API"),
        )
        module.exit_json(changed=True, connection=result)

    except AiDefenseError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
