# -*- coding: utf-8 -*-
# Copyright (c) 2024, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module to schedule recurring validations in Cisco AI Defense."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: validation_schedule
short_description: Schedule recurring AI model validations in Cisco AI Defense
description:
    - Create, update, or delete scheduled recurring validation runs to
      continuously test AI model endpoints against adversarial attacks.
    - Schedules use cron-format expressions so validations can run hourly,
      daily, weekly, or on custom cadences.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    name:
        description:
            - A descriptive name for the validation schedule.
        type: str
        required: true
    model_endpoint:
        description:
            - URL of the AI model endpoint to validate on each scheduled run.
        type: str
        required: true
    schedule:
        description:
            - Cron-format schedule expression defining when validations run.
            - For example C(0 2 * * *) runs daily at 2 AM UTC.
        type: str
        required: true
    categories:
        description:
            - List of validation categories to test on each run.
            - When omitted all available categories are used.
        type: list
        elements: str
        required: false
    schedule_id:
        description:
            - The ID of an existing schedule to update or delete.
        type: str
        required: false
    state:
        description:
            - Whether the schedule should exist or be removed.
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
- name: Schedule daily validation at 2 AM UTC
  stevefulme1.cisco_ai_defense.validation_schedule:
    name: "daily-security-validation"
    model_endpoint: "https://models.example.com/v1/chat/completions"
    schedule: "0 2 * * *"
    categories:
      - prompt_injection
      - data_leakage
    state: present
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"

- name: Schedule weekly compliance check every Monday at 6 AM
  stevefulme1.cisco_ai_defense.validation_schedule:
    name: "weekly-compliance-check"
    model_endpoint: "https://models.example.com/v1/chat/completions"
    schedule: "0 6 * * 1"
    categories:
      - compliance
      - bias
    state: present
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"

- name: Delete a validation schedule
  stevefulme1.cisco_ai_defense.validation_schedule:
    name: "deprecated-schedule"
    model_endpoint: "https://models.example.com/v1/chat/completions"
    schedule: "0 0 * * *"
    schedule_id: "sched-67890"
    state: absent
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"
"""

RETURN = r"""
schedule:
    description: Details of the validation schedule.
    returned: success
    type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.cisco_ai_defense.plugins.module_utils.ai_defense import (
    AiDefenseClient,
)


def main():
    module_args = dict(
        name=dict(type="str", required=True),
        model_endpoint=dict(type="str", required=True),
        schedule=dict(type="str", required=True),
        categories=dict(type="list", elements="str"),
        schedule_id=dict(type="str"),
        state=dict(type="str", choices=["present", "absent"], default="present"),
        api_url=dict(type="str", required=True),
        api_key=dict(type="str", required=True, no_log=True),
        validate_certs=dict(type="bool", default=True),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    client = AiDefenseClient(module)
    state = module.params["state"]
    schedule_id = module.params.get("schedule_id")
    base_path = "/api/v1/validation/schedules"

    # Fetch existing resource if an ID was provided
    existing = None
    if schedule_id:
        existing = client.get(f"{base_path}/{schedule_id}")

    if state == "absent":
        if existing is None:
            module.exit_json(changed=False)
        if module.check_mode:
            module.exit_json(changed=True)
        client.delete(f"{base_path}/{schedule_id}")
        module.exit_json(changed=True)

    payload = {
        "name": module.params["name"],
        "model_endpoint": module.params["model_endpoint"],
        "schedule": module.params["schedule"],
    }
    if module.params.get("categories"):
        payload["categories"] = module.params["categories"]

    if existing is None:
        if module.check_mode:
            module.exit_json(changed=True)
        result = client.post(base_path, payload)
        module.exit_json(changed=True, schedule=result)

    # Update existing
    if module.check_mode:
        module.exit_json(changed=True)
    result = client.put(f"{base_path}/{schedule_id}", payload)
    module.exit_json(changed=True, schedule=result)


if __name__ == "__main__":
    main()
