# -*- coding: utf-8 -*-
# Copyright (c) 2024, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module to generate AI supply chain risk reports via Cisco AI Defense."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: supply_chain_report
short_description: Generate AI supply chain risk reports with Cisco AI Defense
description:
    - Generate comprehensive supply chain risk reports covering AI models,
      container images, and their dependencies.
    - Reports can include a full Software Bill of Materials (SBOM) for
      auditability and compliance purposes.
    - Useful for governance teams to maintain visibility into the AI supply
      chain and identify risks before production deployment.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    report_scope:
        description:
            - Scope of the supply chain report.
            - C(model) covers model provenance and training data lineage.
            - C(container) covers container image analysis and dependencies.
            - C(full) combines both model and container analysis.
        type: str
        choices:
            - model
            - container
            - full
        default: full
    include_sbom:
        description:
            - Whether to include a Software Bill of Materials in the report.
        type: bool
        default: true
    format:
        description:
            - Output format for the generated report.
        type: str
        choices:
            - json
            - pdf
        default: json
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
- name: Generate a full supply chain risk report with SBOM
  stevefulme1.cisco_ai_defense.supply_chain_report:
    report_scope: full
    include_sbom: true
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"
  register: report

- name: Generate a model-only report in PDF format
  stevefulme1.cisco_ai_defense.supply_chain_report:
    report_scope: model
    format: pdf
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"

- name: Container supply chain report without SBOM
  stevefulme1.cisco_ai_defense.supply_chain_report:
    report_scope: container
    include_sbom: false
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"
"""

RETURN = r"""
report:
    description: The generated supply chain risk report.
    returned: success
    type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.cisco_ai_defense.plugins.module_utils.ai_defense import (
    AiDefenseClient,
)


def main():
    module_args = dict(
        report_scope=dict(
            type="str",
            choices=["model", "container", "full"],
            default="full",
        ),
        include_sbom=dict(type="bool", default=True),
        format=dict(type="str", choices=["json", "pdf"], default="json"),
        api_url=dict(type="str", required=True),
        api_key=dict(type="str", required=True, no_log=True),
        validate_certs=dict(type="bool", default=True),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    if module.check_mode:
        module.exit_json(changed=True)

    client = AiDefenseClient(module)

    payload = {
        "report_scope": module.params["report_scope"],
        "include_sbom": module.params["include_sbom"],
        "format": module.params["format"],
    }

    result = client.post("/api/v1/supply_chain/report", payload)
    module.exit_json(changed=True, report=result)


if __name__ == "__main__":
    main()
