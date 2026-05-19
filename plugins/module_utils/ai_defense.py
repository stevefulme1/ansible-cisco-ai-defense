# -*- coding: utf-8 -*-
# Copyright (c) 2024, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Shared HTTP client for Cisco AI Defense API modules."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class AiDefenseClient:
    """HTTP client wrapper for the Cisco AI Defense REST API.

    Provides standardised GET / POST / PUT / DELETE helpers so every module
    uses consistent timeout, certificate-validation and error handling
    behaviour.
    """

    def __init__(self, module):
        if not HAS_REQUESTS:
            module.fail_json(msg="The 'requests' Python package is required.")
        self.module = module
        self.base_url = module.params["api_url"].rstrip("/")
        self.validate_certs = module.params["validate_certs"]
        self.headers = {
            "Authorization": f"Bearer {module.params['api_key']}",
            "Content-Type": "application/json",
        }

    # --------------------------------------------------------------------- #
    # Low-level HTTP helpers
    # --------------------------------------------------------------------- #

    def get(self, path, params=None):
        """Perform a GET request and return parsed JSON (or None on 404)."""
        url = f"{self.base_url}{path}"
        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                verify=self.validate_certs,
                timeout=30,
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            self.module.fail_json(msg=f"GET {path} failed: {exc}")

    def post(self, path, payload=None):
        """Perform a POST request and return parsed JSON."""
        url = f"{self.base_url}{path}"
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                verify=self.validate_certs,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            self.module.fail_json(msg=f"POST {path} failed: {exc}")

    def put(self, path, payload=None):
        """Perform a PUT request and return parsed JSON."""
        url = f"{self.base_url}{path}"
        try:
            response = requests.put(
                url,
                headers=self.headers,
                json=payload,
                verify=self.validate_certs,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            self.module.fail_json(msg=f"PUT {path} failed: {exc}")

    def delete(self, path):
        """Perform a DELETE request."""
        url = f"{self.base_url}{path}"
        try:
            response = requests.delete(
                url,
                headers=self.headers,
                verify=self.validate_certs,
                timeout=30,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            self.module.fail_json(msg=f"DELETE {path} failed: {exc}")
