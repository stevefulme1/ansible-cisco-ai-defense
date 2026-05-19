# -*- coding: utf-8 -*-
# Copyright (c) 2024, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module to validate AI model provenance via Cisco AI Defense."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: model_provenance
short_description: Validate AI model provenance with Cisco AI Defense
description:
    - Verify the provenance, origin, and supply chain integrity of AI models
      before they are deployed to production.
    - Checks cryptographic signatures, training data lineage, and model
      origin to ensure models have not been tampered with.
    - Essential for supply chain security in AI/ML pipelines.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    model_reference:
        description:
            - Reference to the model to validate, such as a model registry URI
              or a HuggingFace model identifier like C(meta-llama/Llama-3-8B).
        type: str
        required: true
    verify_signatures:
        description:
            - Whether to verify cryptographic signatures on the model artifacts.
        type: bool
        default: true
    check_lineage:
        description:
            - Whether to trace the full training data lineage and fine-tuning
              history of the model.
        type: bool
        default: true
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
- name: Validate provenance of a HuggingFace model
  stevefulme1.cisco_ai_defense.model_provenance:
    model_reference: "meta-llama/Llama-3-8B"
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"
  register: provenance

- name: Check provenance without lineage tracing
  stevefulme1.cisco_ai_defense.model_provenance:
    model_reference: "registry.example.com/models/my-classifier:v2.1"
    check_lineage: false
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"

- name: Verify signatures only
  stevefulme1.cisco_ai_defense.model_provenance:
    model_reference: "s3://ml-models/sentiment-analyzer/latest"
    verify_signatures: true
    check_lineage: false
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"
"""

RETURN = r"""
provenance:
    description: Provenance validation results for the model.
    returned: success
    type: dict
    contains:
        origin:
            description: Verified origin of the model (e.g. publisher, repository).
            type: str
            returned: always
        lineage:
            description: Training and fine-tuning lineage information.
            type: dict
            returned: when check_lineage is true
        signature_status:
            description: Result of the cryptographic signature verification.
            type: str
            returned: always
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.cisco_ai_defense.plugins.module_utils.ai_defense import (
    AiDefenseClient,
)


def main():
    module_args = dict(
        model_reference=dict(type="str", required=True),
        verify_signatures=dict(type="bool", default=True),
        check_lineage=dict(type="bool", default=True),
        api_url=dict(type="str", required=True),
        api_key=dict(type="str", required=True, no_log=True),
        validate_certs=dict(type="bool", default=True),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    if module.check_mode:
        module.exit_json(changed=False)

    client = AiDefenseClient(module)

    payload = {
        "model_reference": module.params["model_reference"],
        "verify_signatures": module.params["verify_signatures"],
        "check_lineage": module.params["check_lineage"],
    }

    result = client.post("/api/v1/supply_chain/provenance", payload)
    module.exit_json(changed=False, provenance=result)


if __name__ == "__main__":
    main()
