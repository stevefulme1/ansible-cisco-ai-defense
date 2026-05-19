"""Unit tests for stevefulme1.cisco_ai_defense.policy module."""

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

policy_module = importlib.import_module("policy")


def set_module_args(args):
    """Prepare module args for AnsibleModule."""
    module_utils_basic._ANSIBLE_ARGS = json.dumps(
        {"ANSIBLE_MODULE_ARGS": args}
    ).encode("utf-8")
    module_utils_basic._ANSIBLE_PROFILE = "legacy"


class TestPolicyModule:
    """Comprehensive tests for the policy module."""

    @pytest.fixture(autouse=True)
    def _setup(self, module_args):
        module_args.update({
            "name": "test-policy",
            "policy_type": "input",
            "rules": "block_injection",
            "state": "present",
        })
        set_module_args(module_args)

    def test_create_policy(self):
        get_response = MagicMock()
        get_response.status_code = 404
        get_response.json.return_value = {}

        post_response = MagicMock()
        post_response.status_code = 201
        post_response.json.return_value = {"id": "pol-1", "name": "test-policy"}
        post_response.raise_for_status = MagicMock()

        with patch.object(policy_module, "requests") as mock_requests:
            mock_requests.get.return_value = get_response
            mock_requests.post.return_value = post_response
            mock_requests.RequestException = Exception

            with pytest.raises(SystemExit) as exc_info:
                policy_module.main()
            assert exc_info.value.code == 0
            mock_requests.post.assert_called_once()

    def test_delete_existing_policy(self, module_args):
        module_args.update({"state": "absent", "policy_id": "pol-1"})
        set_module_args(module_args)

        get_response = MagicMock()
        get_response.status_code = 200
        get_response.json.return_value = {"id": "pol-1", "name": "test-policy"}
        get_response.raise_for_status = MagicMock()

        delete_response = MagicMock()
        delete_response.raise_for_status = MagicMock()

        with patch.object(policy_module, "requests") as mock_requests:
            mock_requests.get.return_value = get_response
            mock_requests.delete.return_value = delete_response
            mock_requests.RequestException = Exception

            with pytest.raises(SystemExit) as exc_info:
                policy_module.main()
            assert exc_info.value.code == 0
            mock_requests.delete.assert_called_once()

    def test_delete_absent_noop(self, module_args):
        module_args.update({"state": "absent"})
        set_module_args(module_args)

        with patch.object(policy_module, "requests") as mock_requests:
            mock_requests.RequestException = Exception

            with pytest.raises(SystemExit) as exc_info:
                policy_module.main()
            assert exc_info.value.code == 0

    def test_update_when_changed(self, module_args):
        module_args["policy_id"] = "pol-1"
        set_module_args(module_args)

        get_response = MagicMock()
        get_response.status_code = 200
        get_response.json.return_value = {
            "id": "pol-1",
            "name": "old-name",
            "policy_type": "input",
            "rules": "old_rules",
        }
        get_response.raise_for_status = MagicMock()

        put_response = MagicMock()
        put_response.json.return_value = {"id": "pol-1", "name": "test-policy"}
        put_response.raise_for_status = MagicMock()

        with patch.object(policy_module, "requests") as mock_requests:
            mock_requests.get.return_value = get_response
            mock_requests.put.return_value = put_response
            mock_requests.RequestException = Exception

            with pytest.raises(SystemExit) as exc_info:
                policy_module.main()
            assert exc_info.value.code == 0
            mock_requests.put.assert_called_once()

    def test_no_update_when_unchanged(self, module_args):
        module_args["policy_id"] = "pol-1"
        set_module_args(module_args)

        get_response = MagicMock()
        get_response.status_code = 200
        get_response.json.return_value = {
            "id": "pol-1",
            "name": "test-policy",
            "policy_type": "input",
            "rules": "block_injection",
        }
        get_response.raise_for_status = MagicMock()

        with patch.object(policy_module, "requests") as mock_requests:
            mock_requests.get.return_value = get_response
            mock_requests.RequestException = Exception

            with pytest.raises(SystemExit) as exc_info:
                policy_module.main()
            assert exc_info.value.code == 0
            mock_requests.put.assert_not_called()

    def test_check_mode_create(self, module_args):
        module_args["_ansible_check_mode"] = True
        set_module_args(module_args)

        with patch.object(policy_module, "requests") as mock_requests:
            mock_requests.RequestException = Exception

            with pytest.raises(SystemExit) as exc_info:
                policy_module.main()
            assert exc_info.value.code == 0
            mock_requests.post.assert_not_called()

    def test_api_error_on_create(self):
        with patch.object(policy_module, "requests") as mock_requests:
            mock_requests.get.side_effect = [
                MagicMock(status_code=404, json=MagicMock(return_value={}))
            ]
            mock_requests.post.side_effect = Exception("500 Internal Server Error")
            mock_requests.RequestException = Exception

            with pytest.raises(SystemExit) as exc_info:
                policy_module.main()
            assert exc_info.value.code == 1
