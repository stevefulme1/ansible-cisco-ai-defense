"""Unit tests for runtime policy modules: rate_limit, pii_policy, topic_policy."""

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

rate_limit_module = importlib.import_module("rate_limit")
pii_policy_module = importlib.import_module("pii_policy")
topic_policy_module = importlib.import_module("topic_policy")


def set_module_args(args):
    """Prepare module args for AnsibleModule."""
    module_utils_basic._ANSIBLE_ARGS = json.dumps(
        {"ANSIBLE_MODULE_ARGS": args}
    ).encode("utf-8")
    module_utils_basic._ANSIBLE_PROFILE = "legacy"


# ------------------------------------------------------------------ #
# rate_limit
# ------------------------------------------------------------------ #
class TestRateLimit:

    @pytest.fixture(autouse=True)
    def _setup(self, module_args):
        module_args.update({
            "name": "Chat endpoint limit",
            "endpoint_pattern": "/api/v1/chat/*",
            "requests_per_minute": 60,
            "scope": "per_user",
            "state": "present",
        })
        set_module_args(module_args)

    def test_create_rate_limit(self):
        mc = MagicMock()
        mc.get.return_value = None
        mc.post.return_value = {"id": "rl-1", "name": "Chat endpoint limit"}

        with patch.object(rate_limit_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                rate_limit_module.main()
            assert exc_info.value.code == 0
            mc.post.assert_called_once()

    def test_update_rate_limit(self, module_args):
        module_args["rate_limit_id"] = "rl-1"
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = {
            "id": "rl-1",
            "name": "Old name",
            "endpoint_pattern": "/api/v1/chat/*",
            "requests_per_minute": 30,
            "scope": "per_user",
        }
        mc.put.return_value = {"id": "rl-1", "name": "Chat endpoint limit"}

        with patch.object(rate_limit_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                rate_limit_module.main()
            assert exc_info.value.code == 0
            mc.put.assert_called_once()

    def test_no_update_when_unchanged(self, module_args):
        module_args["rate_limit_id"] = "rl-1"
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = {
            "id": "rl-1",
            "name": "Chat endpoint limit",
            "endpoint_pattern": "/api/v1/chat/*",
            "requests_per_minute": 60,
            "scope": "per_user",
        }

        with patch.object(rate_limit_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                rate_limit_module.main()
            assert exc_info.value.code == 0
            mc.put.assert_not_called()

    def test_delete_rate_limit(self, module_args):
        module_args.update({"state": "absent", "rate_limit_id": "rl-1"})
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = {"id": "rl-1"}

        with patch.object(rate_limit_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                rate_limit_module.main()
            assert exc_info.value.code == 0
            mc.delete.assert_called_once()

    def test_check_mode(self, module_args):
        module_args["_ansible_check_mode"] = True
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = None

        with patch.object(rate_limit_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                rate_limit_module.main()
            assert exc_info.value.code == 0
            mc.post.assert_not_called()

    def test_burst_limit_included(self, module_args):
        module_args["burst_limit"] = 10
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = None
        mc.post.return_value = {"id": "rl-1"}

        with patch.object(rate_limit_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit):
                rate_limit_module.main()
            payload = mc.post.call_args[0][1]
            assert payload["burst_limit"] == 10


# ------------------------------------------------------------------ #
# pii_policy
# ------------------------------------------------------------------ #
class TestPiiPolicy:

    @pytest.fixture(autouse=True)
    def _setup(self, module_args):
        module_args.update({
            "name": "Financial PII",
            "entity_types": ["ssn", "credit_card"],
            "masking_strategy": "redact",
            "state": "present",
        })
        set_module_args(module_args)

    def test_create_pii_policy(self):
        mc = MagicMock()
        mc.get.return_value = None
        mc.post.return_value = {"id": "pii-1", "name": "Financial PII"}

        with patch.object(pii_policy_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                pii_policy_module.main()
            assert exc_info.value.code == 0
            mc.post.assert_called_once()

    def test_delete_pii_policy(self, module_args):
        module_args.update({"state": "absent", "policy_id": "pii-1"})
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = {"id": "pii-1"}

        with patch.object(pii_policy_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                pii_policy_module.main()
            assert exc_info.value.code == 0
            mc.delete.assert_called_once()

    def test_no_update_when_unchanged(self, module_args):
        module_args["policy_id"] = "pii-1"
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = {
            "id": "pii-1",
            "name": "Financial PII",
            "entity_types": ["credit_card", "ssn"],
            "masking_strategy": "redact",
        }

        with patch.object(pii_policy_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                pii_policy_module.main()
            assert exc_info.value.code == 0
            mc.put.assert_not_called()

    def test_exceptions_passed(self, module_args):
        module_args["exceptions"] = ["support@example.com"]
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = None
        mc.post.return_value = {"id": "pii-2"}

        with patch.object(pii_policy_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit):
                pii_policy_module.main()
            payload = mc.post.call_args[0][1]
            assert payload["exceptions"] == ["support@example.com"]


# ------------------------------------------------------------------ #
# topic_policy
# ------------------------------------------------------------------ #
class TestTopicPolicy:

    @pytest.fixture(autouse=True)
    def _setup(self, module_args):
        module_args.update({
            "name": "Safety policy",
            "blocked_topics": ["weapons", "self_harm"],
            "scoring_threshold": 0.75,
            "enforcement_action": "block",
            "state": "present",
        })
        set_module_args(module_args)

    def test_create_topic_policy(self):
        mc = MagicMock()
        mc.get.return_value = None
        mc.post.return_value = {"id": "tp-1", "name": "Safety policy"}

        with patch.object(topic_policy_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                topic_policy_module.main()
            assert exc_info.value.code == 0
            mc.post.assert_called_once()

    def test_delete_topic_policy(self, module_args):
        module_args.update({"state": "absent", "policy_id": "tp-1"})
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = {"id": "tp-1"}

        with patch.object(topic_policy_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                topic_policy_module.main()
            assert exc_info.value.code == 0
            mc.delete.assert_called_once()

    def test_no_update_when_unchanged(self, module_args):
        module_args["policy_id"] = "tp-1"
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = {
            "id": "tp-1",
            "name": "Safety policy",
            "blocked_topics": ["self_harm", "weapons"],
            "scoring_threshold": 0.75,
            "enforcement_action": "block",
        }

        with patch.object(topic_policy_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                topic_policy_module.main()
            assert exc_info.value.code == 0
            mc.put.assert_not_called()

    def test_allowed_topics_in_payload(self, module_args):
        module_args["allowed_topics"] = ["technology", "science"]
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = None
        mc.post.return_value = {"id": "tp-2"}

        with patch.object(topic_policy_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit):
                topic_policy_module.main()
            payload = mc.post.call_args[0][1]
            assert payload["allowed_topics"] == ["technology", "science"]

    def test_check_mode(self, module_args):
        module_args["_ansible_check_mode"] = True
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = None

        with patch.object(topic_policy_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                topic_policy_module.main()
            assert exc_info.value.code == 0
            mc.post.assert_not_called()
