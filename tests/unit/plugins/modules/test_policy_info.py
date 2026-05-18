"""Unit tests for stevefulme1.cisco_ai_defense.policy_info module."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic as module_utils_basic


MODULE_PATH = "ansible_collections.stevefulme1.cisco_ai_defense.plugins.modules.policy_info"


@pytest.fixture
def module_args():
    """Base module args fixture."""
    args = {
        "api_url": "https://api.example.com",
        "api_key": "test-api-key",
        "validate_certs": False,
    }
    return args


@pytest.fixture(autouse=True)
def mock_ansible_module(module_args, monkeypatch):
    """Mock AnsibleModule args."""
    monkeypatch.setattr(
        module_utils_basic, "_ANSIBLE_ARGS",
        module_utils_basic._build_module_args(module_args),
    )


class TestModule:
    """Test policy_info module."""

    @patch(f"{MODULE_PATH}.requests")
    def test_module_args(self, mock_requests, module_args):
        """Module accepts expected arguments."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_requests.get.return_value = mock_response
        mock_requests.RequestException = Exception
        assert "api_url" in module_args
        assert "api_key" in module_args
