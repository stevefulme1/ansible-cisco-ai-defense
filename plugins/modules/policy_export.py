# -*- coding: utf-8 -*-
# Copyright (c) 2024, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for exporting policies from Cisco AI Defense."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: policy_export
short_description: Export policies as structured data from Cisco AI Defense
description:
    - Export one or more policies from Cisco AI Defense as structured YAML or JSON data.
    - Exported data can be used for backup, migration between environments, or
      version-controlled policy-as-code workflows.
    - When no I(policy_ids) are specified all policies in the tenant are exported.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    policy_ids:
        description:
            - List of policy identifiers to export.
            - When omitted or empty, all policies are exported.
        type: list
        elements: str
    export_format:
        description:
            - The output format of the exported data.
        type: str
        choices:
            - yaml
            - json
        default: yaml
    include_assignments:
        description:
            - Whether to include policy-to-target assignment mappings in the export.
        type: bool
        default: false
    dest:
        description:
            - Optional file path where the exported data should be written.
            - When omitted the data is returned in the module result only.
        type: path
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
- name: Export all policies as YAML
  stevefulme1.cisco_ai_defense.policy_export:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    export_format: yaml
    include_assignments: true
  register: export_result

- name: Export specific policies as JSON to a file
  stevefulme1.cisco_ai_defense.policy_export:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    policy_ids:
      - "pol-abc123"
      - "pol-def456"
    export_format: json
    dest: "/tmp/ai_defense_policies.json"

- name: Export all policies for backup
  stevefulme1.cisco_ai_defense.policy_export:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    export_format: yaml
    dest: "/opt/backups/policies_{{ ansible_date_time.date }}.yml"
"""

RETURN = r"""
exported_data:
    description: The exported policy data.
    returned: always
    type: dict
    contains:
        policies:
            description: List of exported policy definitions.
            type: list
            returned: always
        assignments:
            description: Policy assignment mappings (when include_assignments is true).
            type: list
            returned: when include_assignments is true
file_path:
    description: Path to the file where exported data was written.
    returned: when dest is specified
    type: str
"""

import json
import os

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.cisco_ai_defense.plugins.module_utils.ai_defense import (
    AiDefenseClient,
)


def main():
    module_args = dict(
        policy_ids=dict(type="list", elements="str"),
        export_format=dict(type="str", choices=["yaml", "json"], default="yaml"),
        include_assignments=dict(type="bool", default=False),
        dest=dict(type="path"),
        api_url=dict(type="str", required=True),
        api_key=dict(type="str", required=True, no_log=True),
        validate_certs=dict(type="bool", default=True),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    if module.check_mode:
        module.exit_json(changed=False)

    client = AiDefenseClient(module)

    payload = {
        "format": module.params["export_format"],
        "include_assignments": module.params["include_assignments"],
    }
    if module.params.get("policy_ids"):
        payload["policy_ids"] = module.params["policy_ids"]

    exported = client.post("/api/v1/policies/export", payload)

    result = {"changed": False, "exported_data": exported}

    dest = module.params.get("dest")
    if dest:
        # type=path handles expansion automatically
        try:
            with open(dest, "w", encoding="utf-8") as fh:
                if module.params["export_format"] == "json":
                    json.dump(exported, fh, indent=2)
                else:
                    # Write YAML if PyYAML available, fall back to JSON
                    try:
                        import yaml
                        yaml.safe_dump(exported, fh, default_flow_style=False)
                    except ImportError:
                        json.dump(exported, fh, indent=2)
            result["file_path"] = dest
        except OSError as exc:
            module.fail_json(msg=f"Failed to write export file: {exc}")

    module.exit_json(**result)


if __name__ == "__main__":
    main()
