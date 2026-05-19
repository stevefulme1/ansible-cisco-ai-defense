# -*- coding: utf-8 -*-
# Copyright (c) 2024, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module for importing policies into Cisco AI Defense."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: policy_import
short_description: Import policies from definitions into Cisco AI Defense
description:
    - Import policy definitions into Cisco AI Defense from a local file or
      inline data structure.
    - Supports dry-run mode to preview the import without making changes.
    - Conflict resolution controls how existing policies with the same name
      are handled during import.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    source:
        description:
            - Path to a local YAML or JSON file containing policy definitions,
              or an inline dictionary with the policy data.
            - When a file path is provided the module reads and parses the file
              before submitting it to the API.
        type: raw
        required: true
    import_format:
        description:
            - The format of the source data.
        type: str
        choices:
            - yaml
            - json
        default: yaml
    dry_run:
        description:
            - When C(true) the API validates the import payload and returns
              what would be imported without making any changes.
        type: bool
        default: false
    conflict_resolution:
        description:
            - How to handle conflicts when a policy with the same name already exists.
            - C(skip) leaves the existing policy unchanged.
            - C(overwrite) replaces the existing policy with the imported definition.
            - C(rename) imports the policy under a new auto-generated name.
        type: str
        choices:
            - skip
            - overwrite
            - rename
        default: skip
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
- name: Import policies from a YAML file
  stevefulme1.cisco_ai_defense.policy_import:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    source: "/opt/policies/production_policies.yml"
    import_format: yaml
    conflict_resolution: skip
  register: import_result

- name: Dry-run an import to preview changes
  stevefulme1.cisco_ai_defense.policy_import:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    source: "/opt/policies/staging_policies.json"
    import_format: json
    dry_run: true
  register: preview

- name: Import policies and overwrite conflicts
  stevefulme1.cisco_ai_defense.policy_import:
    api_url: "https://ai-defense.example.com"
    api_key: "{{ vault_ai_defense_key }}"
    source:
      policies:
        - name: "Inline PII policy"
          type: pii
          entity_types:
            - ssn
            - credit_card
          masking_strategy: redact
    import_format: yaml
    conflict_resolution: overwrite
"""

RETURN = r"""
import_result:
    description: Summary of the import operation.
    returned: always
    type: dict
    contains:
        imported_count:
            description: Number of policies successfully imported.
            type: int
            returned: always
        skipped_count:
            description: Number of policies skipped due to conflicts.
            type: int
            returned: always
        errors:
            description: List of error messages for failed imports.
            type: list
            elements: str
            returned: always
        dry_run:
            description: Whether this was a dry-run preview.
            type: bool
            returned: always
"""

import json
import os

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.cisco_ai_defense.plugins.module_utils.ai_defense import (
    AiDefenseClient,
)


def load_source(module):
    """Load and parse the policy source data."""
    source = module.params["source"]
    fmt = module.params["import_format"]

    # If source is already a dict/list, use it directly
    if isinstance(source, (dict, list)):
        return source

    # Otherwise treat it as a file path
    source_path = os.path.expanduser(str(source))
    if not os.path.isfile(source_path):
        module.fail_json(msg=f"Source file not found: {source_path}")

    try:
        with open(source_path, "r", encoding="utf-8") as fh:
            content = fh.read()
    except OSError as exc:
        module.fail_json(msg=f"Failed to read source file: {exc}")

    try:
        if fmt == "json":
            return json.loads(content)
        else:
            try:
                import yaml
                return yaml.safe_load(content)
            except ImportError:
                module.fail_json(msg="PyYAML is required to parse YAML source files.")
    except (json.JSONDecodeError, Exception) as exc:
        module.fail_json(msg=f"Failed to parse source data: {exc}")


def main():
    module_args = dict(
        source=dict(type="raw", required=True),
        import_format=dict(type="str", choices=["yaml", "json"], default="yaml"),
        dry_run=dict(type="bool", default=False),
        conflict_resolution=dict(type="str", choices=["skip", "overwrite", "rename"], default="skip"),
        api_url=dict(type="str", required=True),
        api_key=dict(type="str", required=True, no_log=True),
        validate_certs=dict(type="bool", default=True),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    if module.check_mode:
        module.exit_json(changed=False, import_result=dict(
            imported_count=0, skipped_count=0, errors=[], dry_run=True,
        ))

    client = AiDefenseClient(module)
    source_data = load_source(module)

    payload = {
        "data": source_data,
        "format": module.params["import_format"],
        "dry_run": module.params["dry_run"],
        "conflict_resolution": module.params["conflict_resolution"],
    }

    result = client.post("/api/v1/policies/import", payload)

    changed = not module.params["dry_run"] and result.get("imported_count", 0) > 0
    module.exit_json(changed=changed, import_result=result)


if __name__ == "__main__":
    main()
