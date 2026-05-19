"""Unit tests for stevefulme1.cisco_ai_defense.shadow_ai module."""

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

shadow_ai_module = importlib.import_module("shadow_ai")


def set_module_args(args):
    """Prepare module args for AnsibleModule."""
    module_utils_basic._ANSIBLE_ARGS = json.dumps(
        {"ANSIBLE_MODULE_ARGS": args}
    ).encode("utf-8")
    module_utils_basic._ANSIBLE_PROFILE = "legacy"


class TestShadowAiModule:
    """Tests for the shadow_ai module."""

    @pytest.fixture(autouse=True)
    def _setup(self, module_args):
        module_args.update({
            "scan_scope": "full",
            "auto_quarantine": False,
        })
        set_module_args(module_args)

    def test_full_scan_returns_findings(self):
        mock_client = MagicMock()
        mock_client.post.return_value = {
            "findings": [
                {"severity": "high", "asset_name": "rogue-model", "recommendation": "quarantine"}
            ]
        }

        with patch.object(shadow_ai_module, "AiDefenseClient", return_value=mock_client):
            with pytest.raises(SystemExit) as exc_info:
                shadow_ai_module.main()
            assert exc_info.value.code == 0

            mock_client.post.assert_called_once_with(
                "/api/v1/shadow_ai/detect",
                {"scan_scope": "full", "auto_quarantine": False},
            )

    def test_auto_quarantine_passed_to_api(self, module_args):
        module_args.update({
            "scan_scope": "cloud_only",
            "auto_quarantine": True,
        })
        set_module_args(module_args)

        mock_client = MagicMock()
        mock_client.post.return_value = {"findings": []}

        with patch.object(shadow_ai_module, "AiDefenseClient", return_value=mock_client):
            with pytest.raises(SystemExit):
                shadow_ai_module.main()

            payload = mock_client.post.call_args[0][1]
            assert payload["auto_quarantine"] is True

    def test_check_mode_no_api_call(self, module_args):
        module_args.update({
            "scan_scope": "full",
            "_ansible_check_mode": True,
        })
        set_module_args(module_args)

        mock_client = MagicMock()

        with patch.object(shadow_ai_module, "AiDefenseClient", return_value=mock_client):
            with pytest.raises(SystemExit) as exc_info:
                shadow_ai_module.main()
            assert exc_info.value.code == 0
            mock_client.post.assert_not_called()

    def test_list_response_handled(self):
        """API may return a bare list instead of dict with 'findings' key."""
        mock_client = MagicMock()
        mock_client.post.return_value = [
            {"severity": "medium", "asset_name": "test"}
        ]

        with patch.object(shadow_ai_module, "AiDefenseClient", return_value=mock_client):
            with pytest.raises(SystemExit) as exc_info:
                shadow_ai_module.main()
            assert exc_info.value.code == 0

    @pytest.mark.parametrize("scope", ["full", "cloud_only", "on_prem_only"])
    def test_scan_scopes_accepted(self, scope, module_args):
        module_args["scan_scope"] = scope
        set_module_args(module_args)

        mock_client = MagicMock()
        mock_client.post.return_value = {"findings": []}

        with patch.object(shadow_ai_module, "AiDefenseClient", return_value=mock_client):
            with pytest.raises(SystemExit) as exc_info:
                shadow_ai_module.main()
            assert exc_info.value.code == 0
