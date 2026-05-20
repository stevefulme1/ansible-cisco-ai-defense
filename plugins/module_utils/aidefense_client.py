# -*- coding: utf-8 -*-
# Copyright: (c) 2025, Steve Fulmer <sfulmer@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""HTTP client for Cisco AI Defense APIs.

Provides two client classes:
- InspectionClient: for the Runtime Inspection API (content scanning)
- ManagementClient: for the Management API (applications, connections, policies)
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from ansible.module_utils.urls import open_url
from ansible.module_utils.six.moves.urllib.error import HTTPError, URLError
from ansible.module_utils.six.moves.urllib.parse import urlencode

# Region to base-URL mappings (matches cisco-aidefense-sdk config.py)
INSPECTION_ENDPOINTS = {
    "us": "https://us.api.inspect.aidefense.security.cisco.com",
    "eu": "https://eu.api.inspect.aidefense.security.cisco.com",
    "apjc": "https://apj.api.inspect.aidefense.security.cisco.com",
}

MANAGEMENT_ENDPOINTS = {
    "us": "https://us.api.aidefense.security.cisco.com",
    "eu": "https://eu.api.aidefense.security.cisco.com",
    "apjc": "https://ap.api.aidefense.security.cisco.com",
}


class AiDefenseError(Exception):
    """Exception raised by AI Defense API calls."""

    def __init__(self, message, status_code=None, response_body=None):
        super(AiDefenseError, self).__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class InspectionClient(object):
    """Client for the Cisco AI Defense Inspection (Runtime) API.

    Sends chat messages for AI threat inspection via
    ``POST /api/v1/inspect/chat``.

    Args:
        api_key: Connection-level API key (X-Cisco-AI-Defense-API-Key).
        region: One of ``us``, ``eu``, ``apjc``.
        validate_certs: Whether to verify TLS certificates.
        timeout: Request timeout in seconds.
    """

    def __init__(self, api_key, region="us", validate_certs=True, timeout=30):
        self.api_key = api_key
        base = INSPECTION_ENDPOINTS.get(region)
        if base is None:
            raise AiDefenseError("Invalid region '{0}'. Must be one of: {1}".format(
                region, ", ".join(sorted(INSPECTION_ENDPOINTS))
            ))
        self.base_url = base
        self.validate_certs = validate_certs
        self.timeout = timeout

    def inspect_chat(self, messages, metadata=None, config=None):
        """Submit chat messages for AI threat inspection.

        Args:
            messages: List of dicts with ``role`` (user/assistant/system) and ``content``.
            metadata: Optional dict of request metadata (user, src_app, etc.).
            config: Optional dict of inspection config (enabled_rules, etc.).

        Returns:
            dict: Inspection response with classifications, is_safe, action, severity, etc.
        """
        url = "{0}/api/v1/inspect/chat".format(self.base_url)
        payload = {"messages": messages}
        if metadata:
            payload["metadata"] = metadata
        if config:
            payload["config"] = config
        return self._request("POST", url, data=payload)

    def _request(self, method, url, data=None, params=None):
        headers = {
            "X-Cisco-AI-Defense-API-Key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if params:
            url = "{0}?{1}".format(url, urlencode(params))
        body = json.dumps(data) if data else None
        try:
            resp = open_url(
                url,
                method=method,
                headers=headers,
                data=body,
                validate_certs=self.validate_certs,
                timeout=self.timeout,
            )
            resp_body = resp.read()
            if resp_body:
                return json.loads(resp_body)
            return {}
        except HTTPError as e:
            try:
                err_body = e.read()
                err_msg = json.loads(err_body) if err_body else str(e)
            except Exception:
                err_msg = str(e)
            raise AiDefenseError(
                "API request failed: {0}".format(err_msg),
                status_code=e.code,
                response_body=err_msg,
            )
        except URLError as e:
            raise AiDefenseError("Connection error: {0}".format(str(e.reason)))


class ManagementClient(object):
    """Client for the Cisco AI Defense Management API.

    Manages applications, connections, and policies via the Management API
    at ``/api/ai-defense/v1/``.

    Args:
        api_key: Tenant-level API key (X-Cisco-AI-Defense-Tenant-API-Key).
        region: One of ``us``, ``eu``, ``apjc``.
        validate_certs: Whether to verify TLS certificates.
        timeout: Request timeout in seconds.
    """

    API_PREFIX = "api/ai-defense/v1"

    def __init__(self, api_key, region="us", validate_certs=True, timeout=30):
        self.api_key = api_key
        base = MANAGEMENT_ENDPOINTS.get(region)
        if base is None:
            raise AiDefenseError("Invalid region '{0}'. Must be one of: {1}".format(
                region, ", ".join(sorted(MANAGEMENT_ENDPOINTS))
            ))
        self.base_url = "{0}/{1}".format(base.rstrip("/"), self.API_PREFIX)
        self.validate_certs = validate_certs
        self.timeout = timeout

    # ---- Applications ----

    def list_applications(self, limit=None, offset=None):
        """List registered applications."""
        params = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        return self._request("GET", "applications", params=params)

    def get_application(self, application_id):
        """Get a single application by ID."""
        return self._request("GET", "applications/{0}".format(application_id))

    def create_application(self, application_name, description="", connection_type="API"):
        """Create a new application."""
        data = {
            "application_name": application_name,
            "description": description,
            "connection_type": connection_type,
        }
        return self._request("POST", "applications", data=data)

    def update_application(self, application_id, **kwargs):
        """Update an application (application_name, description)."""
        data = {}
        for key in ("application_name", "description"):
            if key in kwargs and kwargs[key] is not None:
                data[key] = kwargs[key]
        if not data:
            raise AiDefenseError("No fields to update")
        return self._request("PUT", "applications/{0}".format(application_id), data=data)

    def delete_application(self, application_id):
        """Delete an application."""
        return self._request("DELETE", "applications/{0}".format(application_id))

    # ---- Connections ----

    def list_connections(self, limit=None, offset=None):
        """List connections."""
        params = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        return self._request("GET", "connections", params=params)

    def get_connection(self, connection_id):
        """Get a single connection by ID."""
        return self._request("GET", "connections/{0}".format(connection_id))

    def create_connection(self, application_id, connection_name, connection_type="API"):
        """Create a new connection."""
        data = {
            "application_id": application_id,
            "connection_name": connection_name,
            "connection_type": connection_type,
        }
        return self._request("POST", "connections", data=data)

    def delete_connection(self, connection_id):
        """Delete a connection."""
        return self._request("DELETE", "connections/{0}".format(connection_id))

    # ---- Policies ----

    def list_policies(self, limit=None, offset=None):
        """List policies."""
        params = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        return self._request("GET", "policies", params=params)

    def get_policy(self, policy_id):
        """Get a single policy by ID."""
        return self._request("GET", "policies/{0}".format(policy_id))

    def update_policy(self, policy_id, **kwargs):
        """Update a policy (name, description, status)."""
        data = {}
        for key in ("name", "description", "status"):
            if key in kwargs and kwargs[key] is not None:
                data[key] = kwargs[key]
        if not data:
            raise AiDefenseError("No fields to update")
        return self._request("PUT", "policies/{0}".format(policy_id), data=data)

    def delete_policy(self, policy_id):
        """Delete a policy."""
        return self._request("DELETE", "policies/{0}".format(policy_id))

    def update_policy_connections(self, policy_id, associate=None, disassociate=None):
        """Associate or disassociate connections with a policy."""
        data = {}
        if associate:
            data["connections_to_associate"] = associate
        if disassociate:
            data["connections_to_disassociate"] = disassociate
        if not data:
            raise AiDefenseError("No connections specified")
        return self._request("POST", "policies/{0}/connections".format(policy_id), data=data)

    # ---- Internal ----

    def _request(self, method, path, data=None, params=None):
        url = "{0}/{1}".format(self.base_url, path)
        headers = {
            "X-Cisco-AI-Defense-Tenant-API-Key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if params:
            url = "{0}?{1}".format(url, urlencode(params))
        body = json.dumps(data) if data else None
        try:
            resp = open_url(
                url,
                method=method,
                headers=headers,
                data=body,
                validate_certs=self.validate_certs,
                timeout=self.timeout,
            )
            resp_body = resp.read()
            if resp_body:
                return json.loads(resp_body)
            return {}
        except HTTPError as e:
            try:
                err_body = e.read()
                err_msg = json.loads(err_body) if err_body else str(e)
            except Exception:
                err_msg = str(e)
            raise AiDefenseError(
                "API request failed: {0}".format(err_msg),
                status_code=e.code,
                response_body=err_msg,
            )
        except URLError as e:
            raise AiDefenseError("Connection error: {0}".format(str(e.reason)))
