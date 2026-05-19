# -*- coding: utf-8 -*-
# Copyright (c) 2024, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible module to scan AI workload containers via Cisco AI Defense."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: container_scan
short_description: Scan AI workload containers with Cisco AI Defense
description:
    - Scan container images that host AI workloads for vulnerabilities,
      misconfigurations, and insecure GPU driver versions.
    - Supports multiple scan depths from a quick surface check to a deep
      layer-by-layer analysis of the container filesystem.
    - Integrates with Cisco AI Defense supply chain security to provide
      a complete picture of container risk.
version_added: "1.1.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    image_reference:
        description:
            - Fully qualified container image reference to scan, such as
              C(registry.example.com/ai-models/llm-service:v1.2.0).
        type: str
        required: true
    scan_depth:
        description:
            - Depth of the container scan.
            - C(quick) checks only the image manifest and known CVEs.
            - C(standard) inspects all layers and installed packages.
            - C(deep) performs full filesystem analysis including GPU driver
              binaries and model artifacts.
        type: str
        choices:
            - quick
            - standard
            - deep
        default: standard
    include_gpu_drivers:
        description:
            - Whether to include GPU driver analysis in the scan.
            - GPU drivers in AI workload containers are a common attack surface.
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
- name: Standard scan of an AI model serving container
  stevefulme1.cisco_ai_defense.container_scan:
    image_reference: "registry.example.com/ai-models/llm-service:v1.2.0"
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"
  register: scan_results

- name: Deep scan including GPU driver analysis
  stevefulme1.cisco_ai_defense.container_scan:
    image_reference: "nvcr.io/nvidia/pytorch:24.01-py3"
    scan_depth: deep
    include_gpu_drivers: true
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"

- name: Quick scan without GPU driver checks
  stevefulme1.cisco_ai_defense.container_scan:
    image_reference: "ghcr.io/org/inference-server:latest"
    scan_depth: quick
    include_gpu_drivers: false
    api_url: "https://aidefense.example.com"
    api_key: "{{ cisco_ai_defense_api_key }}"
"""

RETURN = r"""
scan_results:
    description: Container scan results.
    returned: success
    type: dict
    contains:
        vulnerabilities:
            description: List of vulnerabilities found in the container image.
            type: list
            elements: dict
            returned: always
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.cisco_ai_defense.plugins.module_utils.ai_defense import (
    AiDefenseClient,
)


def main():
    module_args = dict(
        image_reference=dict(type="str", required=True),
        scan_depth=dict(
            type="str",
            choices=["quick", "standard", "deep"],
            default="standard",
        ),
        include_gpu_drivers=dict(type="bool", default=True),
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
        "image_reference": module.params["image_reference"],
        "scan_depth": module.params["scan_depth"],
        "include_gpu_drivers": module.params["include_gpu_drivers"],
    }

    result = client.post("/api/v1/supply_chain/container_scan", payload)
    module.exit_json(changed=False, scan_results=result)


if __name__ == "__main__":
    main()
