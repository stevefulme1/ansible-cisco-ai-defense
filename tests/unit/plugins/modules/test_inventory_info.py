"""Unit tests for stevefulme1.cisco_ai_defense.inventory_info module."""

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

inventory_info_module = importlib.import_module("inventory_info")


def set_module_args(args):
    """Prepare module args for AnsibleModule."""
    module_utils_basic._ANSIBLE_ARGS = json.dumps(
        {"ANSIBLE_MODULE_ARGS": args}
    ).encode("utf-8")
    module_utils_basic._ANSIBLE_PROFILE = "legacy"


class TestInventoryInfoModule:
    """Tests for the inventory_info module."""

    @pytest.fixture(autouse=True)
    def _setup(self, module_args):
        set_module_args(module_args)

    def test_list_all_assets(self):
        mc = MagicMock()
        mc.get.return_value = [
            {"name": "model-1", "type": "model", "risk_level": "high"},
            {"name": "agent-1", "type": "agent", "risk_level": "low"},
        ]

        with patch.object(inventory_info_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                inventory_info_module.main()
            assert exc_info.value.code == 0
            mc.get.assert_called_once()

    def test_filter_by_asset_type(self, module_args):
        module_args["asset_type"] = "model"
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = []

        with patch.object(inventory_info_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                inventory_info_module.main()
            assert exc_info.value.code == 0
            call_kwargs = mc.get.call_args
            assert call_kwargs[1]["params"]["asset_type"] == "model"

    def test_filter_by_risk_and_provider(self, module_args):
        module_args.update({
            "risk_level": "critical",
            "cloud_provider": "aws",
            "limit": 50,
        })
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = []

        with patch.object(inventory_info_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                inventory_info_module.main()
            assert exc_info.value.code == 0
            params = mc.get.call_args[1]["params"]
            assert params["risk_level"] == "critical"
            assert params["cloud_provider"] == "aws"
            assert params["limit"] == 50

    @pytest.mark.parametrize("asset_type", ["model", "agent", "endpoint", "mcp_server"])
    def test_asset_types_accepted(self, asset_type, module_args):
        module_args["asset_type"] = asset_type
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = []

        with patch.object(inventory_info_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                inventory_info_module.main()
            assert exc_info.value.code == 0
