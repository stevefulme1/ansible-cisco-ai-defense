# -*- coding: utf-8 -*-
# Copyright: (c) 2025, Steve Fulmer <sfulmer@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Lookup plugin to retrieve policy details from Cisco AI Defense API."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
name: ai_defense_policy
author: Steve Fulmer (@stevefulme1)
version_added: "1.0.0"
short_description: Look up policy details from Cisco AI Defense
description:
  - Retrieves policy configuration data from the Cisco AI Defense API.
  - Accepts policy names or IDs as lookup terms.
requirements:
  - Network access to the Cisco AI Defense API endpoint
options:
  _terms:
    description: Policy name or ID to look up.
    required: true
    type: str
  api_url:
    description: Base URL for the Cisco AI Defense API.
    type: str
    default: "https://aidefense.cisco.com/api/v1"
    env:
      - name: AI_DEFENSE_API_URL
    ini:
      - section: ai_defense
        key: api_url
  api_key:
    description: API key for authenticating with Cisco AI Defense.
    type: str
    required: true
    env:
      - name: AI_DEFENSE_API_KEY
    ini:
      - section: ai_defense
        key: api_key
  validate_certs:
    description: Whether to validate SSL certificates.
    type: bool
    default: true
  organization_id:
    description: Organization ID to scope the lookup.
    type: str
    env:
      - name: AI_DEFENSE_ORG_ID
    ini:
      - section: ai_defense
        key: organization_id
"""

EXAMPLES = r"""
- name: Look up a policy by name
  ansible.builtin.debug:
    msg: "{{ lookup('stevefulme1.cisco_ai_defense.ai_defense_policy', 'default-input-guardrail', api_key=my_api_key) }}"

- name: Look up multiple policies
  ansible.builtin.debug:
    msg: "{{ lookup('stevefulme1.cisco_ai_defense.ai_defense_policy', 'policy-1', 'policy-2', api_key=my_api_key) }}"

- name: Use policy data in a conditional
  ansible.builtin.debug:
    msg: "Policy is enabled"
  when: (lookup('stevefulme1.cisco_ai_defense.ai_defense_policy', 'my-policy', api_key=my_api_key)).enabled
"""

RETURN = r"""
_raw:
  description: Policy configuration data from Cisco AI Defense.
  type: list
  elements: dict
  contains:
    id:
      description: Policy identifier.
      type: str
    name:
      description: Policy name.
      type: str
    type:
      description: Policy type (input, output).
      type: str
    enabled:
      description: Whether the policy is enabled.
      type: bool
    rules:
      description: List of rules configured for this policy.
      type: list
    created_at:
      description: Policy creation timestamp.
      type: str
    updated_at:
      description: Policy last update timestamp.
      type: str
"""

import json

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.module_utils.urls import open_url


class LookupModule(LookupBase):
    """Look up policy details from Cisco AI Defense API."""

    def run(self, terms, variables=None, **kwargs):
        """Execute the lookup and return policy data.

        Args:
            terms: List of policy names or IDs to look up.
            variables: Ansible variables available to the lookup.
            **kwargs: Additional keyword arguments (api_url, api_key, etc.).

        Returns:
            list: Policy configuration data for each term.

        Raises:
            AnsibleError: If API communication fails or policy is not found.
        """
        self.set_options(var_options=variables, direct=kwargs)

        api_url = self.get_option("api_url")
        api_key = self.get_option("api_key")
        validate_certs = self.get_option("validate_certs")
        organization_id = self.get_option("organization_id")

        if not api_key:
            raise AnsibleError(
                "Cisco AI Defense API key is required. "
                "Set via api_key parameter or AI_DEFENSE_API_KEY environment variable."
            )

        results = []
        for term in terms:
            try:
                policy_data = self._fetch_policy(
                    api_url=api_url,
                    api_key=api_key,
                    validate_certs=validate_certs,
                    organization_id=organization_id,
                    policy_identifier=term,
                )
                results.append(policy_data)
            except Exception as exc:
                raise AnsibleError(
                    f"Failed to look up policy '{term}': {exc}"
                ) from exc

        return results

    @staticmethod
    def _fetch_policy(api_url, api_key, validate_certs, organization_id, policy_identifier):
        """Fetch policy data from the AI Defense API.

        Args:
            api_url: Base API URL.
            api_key: Authentication API key.
            validate_certs: Whether to verify SSL certificates.
            organization_id: Organization ID for scoping.
            policy_identifier: Policy name or ID.

        Returns:
            dict: Policy configuration data.

        Raises:
            AnsibleError: If the API request fails.
        """
        url = f"{api_url}/policies/{policy_identifier}"
        if organization_id:
            url = f"{api_url}/organizations/{organization_id}/policies/{policy_identifier}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        try:
            response = open_url(
                url,
                headers=headers,
                validate_certs=validate_certs,
                method="GET",
            )
            return json.loads(response.read())
        except Exception as exc:
            raise AnsibleError(
                f"API request to {url} failed: {exc}"
            ) from exc
