"""Unit tests for policy management modules: policy_assignment, policy_export, policy_import."""

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

policy_assignment_module = importlib.import_module("policy_assignment")
policy_export_module = importlib.import_module("policy_export")
policy_import_module = importlib.import_module("policy_import")


def set_module_args(args):
    """Prepare module args for AnsibleModule."""
    module_utils_basic._ANSIBLE_ARGS = json.dumps(
        {"ANSIBLE_MODULE_ARGS": args}
    ).encode("utf-8")
    module_utils_basic._ANSIBLE_PROFILE = "legacy"


# ------------------------------------------------------------------ #
# policy_assignment
# ------------------------------------------------------------------ #
class TestPolicyAssignment:

    @pytest.fixture(autouse=True)
    def _setup(self, module_args):
        module_args.update({
            "policy_id": "pol-abc123",
            "target_type": "endpoint",
            "target_id": "ep-chat-prod",
            "inherit_parent": True,
            "state": "present",
        })
        set_module_args(module_args)

    def test_create_assignment(self):
        mc = MagicMock()
        mc.get.return_value = None
        mc.post.return_value = {"id": "asgn-1", "policy_id": "pol-abc123"}

        with patch.object(policy_assignment_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                policy_assignment_module.main()
            assert exc_info.value.code == 0
            mc.post.assert_called_once()

    def test_update_assignment(self, module_args):
        module_args["assignment_id"] = "asgn-1"
        module_args["inherit_parent"] = False
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = {
            "id": "asgn-1",
            "policy_id": "pol-abc123",
            "target_type": "endpoint",
            "target_id": "ep-chat-prod",
            "inherit_parent": True,
        }
        mc.put.return_value = {"id": "asgn-1", "inherit_parent": False}

        with patch.object(policy_assignment_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                policy_assignment_module.main()
            assert exc_info.value.code == 0
            mc.put.assert_called_once()

    def test_delete_assignment(self, module_args):
        module_args.update({"state": "absent", "assignment_id": "asgn-1"})
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = {"id": "asgn-1"}

        with patch.object(policy_assignment_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                policy_assignment_module.main()
            assert exc_info.value.code == 0
            mc.delete.assert_called_once()

    def test_check_mode(self, module_args):
        module_args["_ansible_check_mode"] = True
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = None

        with patch.object(policy_assignment_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                policy_assignment_module.main()
            assert exc_info.value.code == 0
            mc.post.assert_not_called()

    @pytest.mark.parametrize("target_type", ["endpoint", "model", "application", "group"])
    def test_target_types_accepted(self, target_type, module_args):
        module_args["target_type"] = target_type
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = None
        mc.post.return_value = {"id": "a1"}

        with patch.object(policy_assignment_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                policy_assignment_module.main()
            assert exc_info.value.code == 0


# ------------------------------------------------------------------ #
# policy_export
# ------------------------------------------------------------------ #
class TestPolicyExport:

    @pytest.fixture(autouse=True)
    def _setup(self, module_args):
        module_args.update({
            "export_format": "yaml",
            "include_assignments": False,
        })
        set_module_args(module_args)

    def test_export_all(self):
        mc = MagicMock()
        mc.post.return_value = {"policies": [{"name": "pol1"}]}

        with patch.object(policy_export_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                policy_export_module.main()
            assert exc_info.value.code == 0
            mc.post.assert_called_once()

    def test_export_specific_ids(self, module_args):
        module_args["policy_ids"] = ["pol-1", "pol-2"]
        set_module_args(module_args)
        mc = MagicMock()
        mc.post.return_value = {"policies": []}

        with patch.object(policy_export_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit):
                policy_export_module.main()
            payload = mc.post.call_args[0][1]
            assert payload["policy_ids"] == ["pol-1", "pol-2"]

    def test_check_mode(self, module_args):
        module_args["_ansible_check_mode"] = True
        set_module_args(module_args)
        mc = MagicMock()

        with patch.object(policy_export_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                policy_export_module.main()
            assert exc_info.value.code == 0
            mc.post.assert_not_called()

    def test_export_to_file(self, module_args, tmp_path):
        dest = str(tmp_path / "export.json")
        module_args.update({"export_format": "json", "dest": dest})
        set_module_args(module_args)
        mc = MagicMock()
        mc.post.return_value = {"policies": [{"name": "pol1"}]}

        with patch.object(policy_export_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                policy_export_module.main()
            assert exc_info.value.code == 0

            with open(dest) as f:
                data = json.load(f)
            assert "policies" in data


# ------------------------------------------------------------------ #
# policy_import
# ------------------------------------------------------------------ #
class TestPolicyImport:

    @pytest.fixture(autouse=True)
    def _setup(self, module_args):
        module_args.update({
            "source": {"policies": [{"name": "inline"}]},
            "import_format": "yaml",
            "dry_run": False,
            "conflict_resolution": "skip",
        })
        set_module_args(module_args)

    def test_import_inline_data(self):
        mc = MagicMock()
        mc.post.return_value = {"imported_count": 1, "skipped_count": 0, "errors": []}

        with patch.object(policy_import_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                policy_import_module.main()
            assert exc_info.value.code == 0
            mc.post.assert_called_once()

    def test_dry_run(self, module_args):
        module_args["dry_run"] = True
        set_module_args(module_args)
        mc = MagicMock()
        mc.post.return_value = {"imported_count": 0, "skipped_count": 0, "errors": [], "dry_run": True}

        with patch.object(policy_import_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                policy_import_module.main()
            assert exc_info.value.code == 0

    def test_check_mode(self, module_args):
        module_args["_ansible_check_mode"] = True
        set_module_args(module_args)
        mc = MagicMock()

        with patch.object(policy_import_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                policy_import_module.main()
            assert exc_info.value.code == 0
            mc.post.assert_not_called()

    def test_import_from_json_file(self, module_args, tmp_path):
        src = tmp_path / "policies.json"
        src.write_text(json.dumps({"policies": [{"name": "file-policy"}]}))

        module_args.update({
            "source": str(src),
            "import_format": "json",
        })
        set_module_args(module_args)
        mc = MagicMock()
        mc.post.return_value = {"imported_count": 1, "skipped_count": 0, "errors": []}

        with patch.object(policy_import_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                policy_import_module.main()
            assert exc_info.value.code == 0

    @pytest.mark.parametrize("resolution", ["skip", "overwrite", "rename"])
    def test_conflict_resolutions(self, resolution, module_args):
        module_args["conflict_resolution"] = resolution
        set_module_args(module_args)
        mc = MagicMock()
        mc.post.return_value = {"imported_count": 0, "skipped_count": 0, "errors": []}

        with patch.object(policy_import_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                policy_import_module.main()
            assert exc_info.value.code == 0
