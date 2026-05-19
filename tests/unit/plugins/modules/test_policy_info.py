"""Unit tests for stevefulme1.cisco_ai_defense.policy_info module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import importlib
import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic as module_utils_basic

# Add plugins path so we can import modules directly
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", "plugins", "modules"
    ),
)

policy_info_module = importlib.import_module("policy_info")


def set_module_args(args):
    """Prepare module args for AnsibleModule."""
    module_utils_basic._ANSIBLE_ARGS = json.dumps(
        {"ANSIBLE_MODULE_ARGS": args}
    ).encode("utf-8")
    module_utils_basic._ANSIBLE_PROFILE = "legacy"


class TestPolicyInfoModule:
    """Comprehensive tests for the policy_info module."""

    @pytest.fixture(autouse=True)
    def _setup(self, module_args):
        set_module_args(module_args)

    def test_returns_policy_list(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "pol-1", "name": "policy-1", "enabled": True},
            {"id": "pol-2", "name": "policy-2", "enabled": False},
        ]
        mock_response.raise_for_status = MagicMock()

        with patch.object(policy_info_module, "requests") as mock_requests:
            mock_requests.get.return_value = mock_response
            mock_requests.RequestException = Exception

            with pytest.raises(SystemExit) as exc_info:
                policy_info_module.main()
            assert exc_info.value.code == 0
            mock_requests.get.assert_called_once()

    def test_api_error_fails(self):
        with patch.object(policy_info_module, "requests") as mock_requests:
            mock_requests.get.side_effect = Exception("connection refused")
            mock_requests.RequestException = Exception

            with pytest.raises(SystemExit) as exc_info:
                policy_info_module.main()
            assert exc_info.value.code == 1

    def test_empty_result(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_response.raise_for_status = MagicMock()

        with patch.object(policy_info_module, "requests") as mock_requests:
            mock_requests.get.return_value = mock_response
            mock_requests.RequestException = Exception

            with pytest.raises(SystemExit) as exc_info:
                policy_info_module.main()
            assert exc_info.value.code == 0

    def test_api_url_constructed_correctly(self, module_args):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_response.raise_for_status = MagicMock()

        with patch.object(policy_info_module, "requests") as mock_requests:
            mock_requests.get.return_value = mock_response
            mock_requests.RequestException = Exception

            with pytest.raises(SystemExit):
                policy_info_module.main()

            call_args = mock_requests.get.call_args
            url = call_args[0][0]
            assert "/api/v1/" in url

    def test_module_args_present(self, module_args):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_response.raise_for_status = MagicMock()

        with patch.object(policy_info_module, "requests") as mock_requests:
            mock_requests.get.return_value = mock_response
            mock_requests.RequestException = Exception

            assert "api_url" in module_args
            assert "api_key" in module_args
            assert "validate_certs" in module_args
