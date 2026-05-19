"""Unit tests for stevefulme1.cisco_ai_defense.guardrail_rule module."""

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

guardrail_rule_module = importlib.import_module("guardrail_rule")


def set_module_args(args):
    """Prepare module args for AnsibleModule."""
    module_utils_basic._ANSIBLE_ARGS = json.dumps(
        {"ANSIBLE_MODULE_ARGS": args}
    ).encode("utf-8")
    module_utils_basic._ANSIBLE_PROFILE = "legacy"


class TestGuardrailRuleModule:
    """Tests for guardrail_rule module."""

    @pytest.fixture(autouse=True)
    def _setup(self, module_args):
        module_args.update({
            "guardrail_id": "grd-abc123",
            "name": "Block prompt injection",
            "rule_type": "prompt_injection",
            "action": "block",
            "priority": 10,
            "state": "present",
        })
        set_module_args(module_args)

    def test_create_rule(self):
        mc = MagicMock()
        mc.get.return_value = None
        mc.post.return_value = {"id": "rule-1", "name": "Block prompt injection"}

        with patch.object(guardrail_rule_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                guardrail_rule_module.main()
            assert exc_info.value.code == 0
            mc.post.assert_called_once()

    def test_update_rule(self, module_args):
        module_args["rule_id"] = "rule-1"
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = {
            "id": "rule-1",
            "name": "Old name",
            "rule_type": "prompt_injection",
            "action": "block",
            "priority": 10,
        }
        mc.put.return_value = {"id": "rule-1", "name": "Block prompt injection"}

        with patch.object(guardrail_rule_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                guardrail_rule_module.main()
            assert exc_info.value.code == 0
            mc.put.assert_called_once()

    def test_no_update_when_unchanged(self, module_args):
        module_args["rule_id"] = "rule-1"
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = {
            "id": "rule-1",
            "name": "Block prompt injection",
            "rule_type": "prompt_injection",
            "action": "block",
            "priority": 10,
        }

        with patch.object(guardrail_rule_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                guardrail_rule_module.main()
            assert exc_info.value.code == 0
            mc.put.assert_not_called()
            mc.post.assert_not_called()

    def test_delete_rule(self, module_args):
        module_args.update({"state": "absent", "rule_id": "rule-1"})
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = {"id": "rule-1"}

        with patch.object(guardrail_rule_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                guardrail_rule_module.main()
            assert exc_info.value.code == 0
            mc.delete.assert_called_once()

    def test_delete_absent_noop(self, module_args):
        module_args.update({"state": "absent"})
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = None

        with patch.object(guardrail_rule_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                guardrail_rule_module.main()
            assert exc_info.value.code == 0
            mc.delete.assert_not_called()

    def test_check_mode_create(self, module_args):
        module_args["_ansible_check_mode"] = True
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = None

        with patch.object(guardrail_rule_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                guardrail_rule_module.main()
            assert exc_info.value.code == 0
            mc.post.assert_not_called()

    @pytest.mark.parametrize("rule_type", [
        "prompt_injection", "pii_detection", "topic_drift",
        "content_filter", "data_leakage",
    ])
    def test_rule_types_accepted(self, rule_type, module_args):
        module_args["rule_type"] = rule_type
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = None
        mc.post.return_value = {"id": "r1"}

        with patch.object(guardrail_rule_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                guardrail_rule_module.main()
            assert exc_info.value.code == 0

    def test_configuration_dict_passed(self, module_args):
        module_args["configuration"] = {"sensitivity": "high"}
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = None
        mc.post.return_value = {"id": "r1"}

        with patch.object(guardrail_rule_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit):
                guardrail_rule_module.main()

            payload = mc.post.call_args[0][1]
            assert payload["configuration"] == {"sensitivity": "high"}
