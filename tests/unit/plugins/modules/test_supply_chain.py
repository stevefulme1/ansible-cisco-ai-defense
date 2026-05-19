"""Unit tests for supply chain modules: model_provenance, container_scan,
supply_chain_report, supply_chain_report_info."""

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

model_provenance_module = importlib.import_module("model_provenance")
container_scan_module = importlib.import_module("container_scan")
supply_chain_report_module = importlib.import_module("supply_chain_report")
supply_chain_report_info_module = importlib.import_module("supply_chain_report_info")


def set_module_args(args):
    """Prepare module args for AnsibleModule."""
    module_utils_basic._ANSIBLE_ARGS = json.dumps(
        {"ANSIBLE_MODULE_ARGS": args}
    ).encode("utf-8")
    module_utils_basic._ANSIBLE_PROFILE = "legacy"


# ------------------------------------------------------------------ #
# model_provenance
# ------------------------------------------------------------------ #
class TestModelProvenance:

    @pytest.fixture(autouse=True)
    def _setup(self, module_args):
        module_args.update({
            "model_reference": "meta-llama/Llama-3-8B",
            "verify_signatures": True,
            "check_lineage": True,
        })
        set_module_args(module_args)

    def test_provenance_returned(self):
        mc = MagicMock()
        mc.post.return_value = {
            "origin": "HuggingFace",
            "signature_status": "valid",
            "lineage": {"dataset": "c4"},
        }

        with patch.object(model_provenance_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                model_provenance_module.main()
            assert exc_info.value.code == 0
            mc.post.assert_called_once()

    def test_check_mode(self, module_args):
        module_args["_ansible_check_mode"] = True
        set_module_args(module_args)
        mc = MagicMock()

        with patch.object(model_provenance_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                model_provenance_module.main()
            assert exc_info.value.code == 0
            mc.post.assert_not_called()


# ------------------------------------------------------------------ #
# container_scan
# ------------------------------------------------------------------ #
class TestContainerScan:

    @pytest.fixture(autouse=True)
    def _setup(self, module_args):
        module_args.update({
            "image_reference": "registry.example.com/ai/llm:v1",
            "scan_depth": "standard",
            "include_gpu_drivers": True,
        })
        set_module_args(module_args)

    def test_scan_returns_results(self):
        mc = MagicMock()
        mc.post.return_value = {"vulnerabilities": [{"cve": "CVE-2024-0001"}]}

        with patch.object(container_scan_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                container_scan_module.main()
            assert exc_info.value.code == 0
            mc.post.assert_called_once()

    @pytest.mark.parametrize("depth", ["quick", "standard", "deep"])
    def test_scan_depths(self, depth, module_args):
        module_args["scan_depth"] = depth
        set_module_args(module_args)
        mc = MagicMock()
        mc.post.return_value = {"vulnerabilities": []}

        with patch.object(container_scan_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                container_scan_module.main()
            assert exc_info.value.code == 0

    def test_check_mode(self, module_args):
        module_args["_ansible_check_mode"] = True
        set_module_args(module_args)
        mc = MagicMock()

        with patch.object(container_scan_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                container_scan_module.main()
            assert exc_info.value.code == 0
            mc.post.assert_not_called()


# ------------------------------------------------------------------ #
# supply_chain_report
# ------------------------------------------------------------------ #
class TestSupplyChainReport:

    @pytest.fixture(autouse=True)
    def _setup(self, module_args):
        module_args.update({
            "report_scope": "full",
            "include_sbom": True,
            "format": "json",
        })
        set_module_args(module_args)

    def test_report_created(self):
        mc = MagicMock()
        mc.post.return_value = {"report_id": "rpt-1", "status": "completed"}

        with patch.object(supply_chain_report_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                supply_chain_report_module.main()
            assert exc_info.value.code == 0

    def test_check_mode(self, module_args):
        module_args["_ansible_check_mode"] = True
        set_module_args(module_args)
        mc = MagicMock()

        with patch.object(supply_chain_report_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                supply_chain_report_module.main()
            assert exc_info.value.code == 0
            mc.post.assert_not_called()


# ------------------------------------------------------------------ #
# supply_chain_report_info
# ------------------------------------------------------------------ #
class TestSupplyChainReportInfo:

    @pytest.fixture(autouse=True)
    def _setup(self, module_args):
        set_module_args(module_args)

    def test_list_all_reports(self, module_args):
        mc = MagicMock()
        mc.get.return_value = {"reports": [{"id": "r1"}, {"id": "r2"}]}

        with patch.object(supply_chain_report_info_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                supply_chain_report_info_module.main()
            assert exc_info.value.code == 0
            mc.get.assert_called_once()

    def test_get_single_report(self, module_args):
        module_args["report_id"] = "rpt-abc123"
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = {"id": "rpt-abc123", "status": "completed"}

        with patch.object(supply_chain_report_info_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                supply_chain_report_info_module.main()
            assert exc_info.value.code == 0

    def test_report_not_found(self, module_args):
        module_args["report_id"] = "nonexistent"
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = None

        with patch.object(supply_chain_report_info_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                supply_chain_report_info_module.main()
            assert exc_info.value.code == 1

    def test_filter_by_status(self, module_args):
        module_args["status"] = "completed"
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = {"reports": []}

        with patch.object(supply_chain_report_info_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                supply_chain_report_info_module.main()
            assert exc_info.value.code == 0
            call_kwargs = mc.get.call_args
            assert call_kwargs[1]["params"]["status"] == "completed"
