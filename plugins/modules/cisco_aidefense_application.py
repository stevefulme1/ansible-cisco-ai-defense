# -*- coding: utf-8 -*-
# Copyright: (c) 2025, Steve Fulmer <sfulmer@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: cisco_aidefense_application
short_description: Manage applications in Cisco AI Defense
version_added: "0.1.0"
description:
  - Create, update, or delete applications registered in Cisco AI Defense.
  - Applications represent the AI-powered services being protected.
  - Uses the Management API at /api/ai-defense/v1/applications.
author:
  - Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.cisco_ai_defense.aidefense
options:
  state:
    description:
      - Desired state of the application.
    type: str
    default: present
    choices:
      - present
      - absent
  application_id:
    description:
      - The UUID of an existing application.
      - Required when C(state=absent) or when updating an existing application.
    type: str
    required: false
  application_name:
    description:
      - Name of the application.
      - Required when C(state=present) and creating a new application.
    type: str
    required: false
  description:
    description:
      - Description of the application.
    type: str
    required: false
    default: ""
  connection_type:
    description:
      - Type of connection for the application.
    type: str
    required: false
    default: API
    choices:
      - API
      - Gateway
"""

EXAMPLES = r"""
- name: Create an application
  stevefulme1.cisco_ai_defense.cisco_aidefense_application:
    api_key: "{{ aidefense_tenant_key }}"
    application_name: "Customer Chatbot"
    description: "Production chatbot using GPT-4"
    connection_type: API
  register: app

- name: Update an application description
  stevefulme1.cisco_ai_defense.cisco_aidefense_application:
    api_key: "{{ aidefense_tenant_key }}"
    application_id: "{{ app.application.application_id }}"
    application_name: "Customer Chatbot"
    description: "Updated description"

- name: Delete an application
  stevefulme1.cisco_ai_defense.cisco_aidefense_application:
    api_key: "{{ aidefense_tenant_key }}"
    application_id: "{{ app.application.application_id }}"
    state: absent
"""

RETURN = r"""
application:
  description: The application object returned from the API.
  type: dict
  returned: when state is present
  contains:
    application_id:
      description: UUID of the application.
      type: str
    application_name:
      description: Name of the application.
      type: str
    description:
      description: Description of the application.
      type: str
    connection_type:
      description: Connection type (API or Gateway).
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
        application_id=dict(type="str", required=False, default=None),
        application_name=dict(type="str", required=False, default=None),
        description=dict(type="str", required=False, default=""),
        connection_type=dict(type="str", required=False, default="API", choices=["API", "Gateway"]),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[
            ("state", "absent", ("application_id",)),
        ],
        supports_check_mode=True,
    )

    from ansible_collections.stevefulme1.cisco_ai_defense.plugins.module_utils.aidefense_client import (
        ManagementClient,
        AiDefenseError,
    )

    state = module.params["state"]
    application_id = module.params.get("application_id")

    try:
        client = ManagementClient(
            api_key=module.params["api_key"],
            region=module.params["region"],
            validate_certs=module.params["validate_certs"],
            timeout=module.params["timeout"],
        )

        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True, msg="Would delete application.")
            client.delete_application(application_id)
            module.exit_json(changed=True, msg="Application deleted.")

        # state == present
        if application_id:
            # Update existing
            if module.check_mode:
                module.exit_json(changed=True, msg="Would update application.")
            client.update_application(
                application_id,
                application_name=module.params.get("application_name"),
                description=module.params.get("description"),
            )
            result = client.get_application(application_id)
            module.exit_json(changed=True, application=result)
        else:
            # Create new
            if not module.params.get("application_name"):
                module.fail_json(msg="application_name is required when creating a new application.")
            if module.check_mode:
                module.exit_json(changed=True, msg="Would create application.")
            result = client.create_application(
                application_name=module.params["application_name"],
                description=module.params.get("description", ""),
                connection_type=module.params.get("connection_type", "API"),
            )
            module.exit_json(changed=True, application=result)

    except AiDefenseError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
