"""Unit tests for stevefulme1.cisco_ai_defense.discovery module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import importlib
import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic as module_utils_basic

# Add plugins paths so we can import modules and module_utils directly
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", "plugins", "module_utils"
    ),
)
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", "plugins", "modules"
    ),
)

discovery_module = importlib.import_module("discovery")


def set_module_args(args):
    """Prepare module args for AnsibleModule."""
    module_utils_basic._ANSIBLE_ARGS = json.dumps(
        {"ANSIBLE_MODULE_ARGS": args}
    ).encode("utf-8")
    module_utils_basic._ANSIBLE_PROFILE = "legacy"


class TestDiscoveryModule:
    """Tests for the discovery module."""

    @pytest.fixture(autouse=True)
    def _setup(self, module_args):
        module_args.update({
            "scan_type": "full",
            "state": "present",
        })
        set_module_args(module_args)

    def test_full_scan_triggers_post(self):
        mock_client = MagicMock()
        mock_client.post.return_value = {
            "scan_id": "scan-001",
            "status": "running",
            "discovered_count": 0,
        }

        with patch.object(discovery_module, "AiDefenseClient", return_value=mock_client):
            with pytest.raises(SystemExit) as exc_info:
                discovery_module.main()
            assert exc_info.value.code == 0

            mock_client.post.assert_called_once_with(
                "/api/v1/discovery/scans",
                {"scan_type": "full"},
            )

    def test_targeted_scan_includes_provider_and_region(self, module_args):
        module_args.update({
            "scan_type": "targeted",
            "cloud_provider": "aws",
            "region": "us-east-1",
            "state": "present",
        })
        set_module_args(module_args)

        mock_client = MagicMock()
        mock_client.post.return_value = {"scan_id": "scan-002", "status": "running"}

        with patch.object(discovery_module, "AiDefenseClient", return_value=mock_client):
            with pytest.raises(SystemExit):
                discovery_module.main()

            call_payload = mock_client.post.call_args[0][1]
            assert call_payload["cloud_provider"] == "aws"
            assert call_payload["region"] == "us-east-1"

    def test_check_mode_returns_changed_without_api_call(self, module_args):
        module_args.update({
            "scan_type": "incremental",
            "state": "present",
            "_ansible_check_mode": True,
        })
        set_module_args(module_args)

        mock_client = MagicMock()

        with patch.object(discovery_module, "AiDefenseClient", return_value=mock_client):
            with pytest.raises(SystemExit) as exc_info:
                discovery_module.main()
            assert exc_info.value.code == 0
            mock_client.post.assert_not_called()

    @pytest.mark.parametrize("scan_type", ["full", "incremental", "targeted"])
    def test_scan_types_accepted(self, scan_type, module_args):
        module_args["scan_type"] = scan_type
        if scan_type == "targeted":
            module_args["cloud_provider"] = "gcp"
        set_module_args(module_args)

        mock_client = MagicMock()
        mock_client.post.return_value = {"scan_id": "s1"}

        with patch.object(discovery_module, "AiDefenseClient", return_value=mock_client):
            with pytest.raises(SystemExit) as exc_info:
                discovery_module.main()
            assert exc_info.value.code == 0
