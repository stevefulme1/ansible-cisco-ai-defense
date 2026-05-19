"""Unit tests for monitoring modules: metrics_info, splunk_integration, audit_log_info."""

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

metrics_info_module = importlib.import_module("metrics_info")
splunk_integration_module = importlib.import_module("splunk_integration")
audit_log_info_module = importlib.import_module("audit_log_info")


def set_module_args(args):
    """Prepare module args for AnsibleModule."""
    module_utils_basic._ANSIBLE_ARGS = json.dumps(
        {"ANSIBLE_MODULE_ARGS": args}
    ).encode("utf-8")
    module_utils_basic._ANSIBLE_PROFILE = "legacy"


# ------------------------------------------------------------------ #
# metrics_info (uses AiDefenseClient)
# ------------------------------------------------------------------ #
class TestMetricsInfo:

    @pytest.fixture(autouse=True)
    def _setup(self, module_args):
        module_args.update({
            "time_range": "24h",
        })
        set_module_args(module_args)

    def test_returns_metrics(self):
        mc = MagicMock()
        mc.get.return_value = {
            "metric_type": "all",
            "time_range": "24h",
            "data_points": [{"timestamp": "2025-01-01", "value": 42}],
        }

        with patch.object(metrics_info_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                metrics_info_module.main()
            assert exc_info.value.code == 0
            mc.get.assert_called_once()

    def test_filter_by_type_and_group(self, module_args):
        module_args.update({
            "metric_type": "blocked_requests",
            "group_by": "endpoint",
            "time_range": "7d",
        })
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = {"data_points": []}

        with patch.object(metrics_info_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                metrics_info_module.main()
            assert exc_info.value.code == 0
            call_kwargs = mc.get.call_args
            assert call_kwargs[1]["params"]["metric_type"] == "blocked_requests"
            assert call_kwargs[1]["params"]["group_by"] == "endpoint"

    @pytest.mark.parametrize("time_range", ["1h", "24h", "7d", "30d", "90d"])
    def test_time_ranges_accepted(self, time_range, module_args):
        module_args["time_range"] = time_range
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = {"data_points": []}

        with patch.object(metrics_info_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                metrics_info_module.main()
            assert exc_info.value.code == 0


# ------------------------------------------------------------------ #
# splunk_integration (uses AiDefenseClient)
# ------------------------------------------------------------------ #
class TestSplunkIntegration:

    @pytest.fixture(autouse=True)
    def _setup(self, module_args):
        module_args.update({
            "name": "Prod Splunk",
            "splunk_url": "https://splunk.example.com:8088/services/collector",
            "splunk_token": "hec-token-secret",
            "severity_filter": "all",
            "index_name": "cisco_ai_defense",
            "state": "present",
        })
        set_module_args(module_args)

    def test_create_integration(self):
        mc = MagicMock()
        mc.get.return_value = None
        mc.post.return_value = {"id": "int-1", "name": "Prod Splunk"}

        with patch.object(splunk_integration_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                splunk_integration_module.main()
            assert exc_info.value.code == 0
            mc.post.assert_called_once()

    def test_delete_integration(self, module_args):
        module_args.update({"state": "absent", "integration_id": "int-1"})
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = {"id": "int-1"}

        with patch.object(splunk_integration_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                splunk_integration_module.main()
            assert exc_info.value.code == 0
            mc.delete.assert_called_once()

    def test_update_always_when_token_present(self, module_args):
        """splunk_token is no_log so needs_update always returns True."""
        module_args["integration_id"] = "int-1"
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = {
            "id": "int-1",
            "name": "Prod Splunk",
            "splunk_url": "https://splunk.example.com:8088/services/collector",
            "severity_filter": "all",
            "index_name": "cisco_ai_defense",
        }
        mc.put.return_value = {"id": "int-1"}

        with patch.object(splunk_integration_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                splunk_integration_module.main()
            assert exc_info.value.code == 0
            mc.put.assert_called_once()

    def test_event_types_in_payload(self, module_args):
        module_args["event_types"] = ["threats", "audit_events"]
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = None
        mc.post.return_value = {"id": "int-2"}

        with patch.object(splunk_integration_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit):
                splunk_integration_module.main()
            payload = mc.post.call_args[0][1]
            assert payload["event_types"] == ["threats", "audit_events"]

    def test_check_mode(self, module_args):
        module_args["_ansible_check_mode"] = True
        set_module_args(module_args)
        mc = MagicMock()
        mc.get.return_value = None

        with patch.object(splunk_integration_module, "AiDefenseClient", return_value=mc):
            with pytest.raises(SystemExit) as exc_info:
                splunk_integration_module.main()
            assert exc_info.value.code == 0
            mc.post.assert_not_called()


# ------------------------------------------------------------------ #
# audit_log_info (uses inline requests)
# ------------------------------------------------------------------ #
class TestAuditLogInfo:

    @pytest.fixture(autouse=True)
    def _setup(self, module_args):
        set_module_args(module_args)

    def test_returns_audit_logs(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"event": "policy_updated", "timestamp": "2025-01-01"}]
        mock_response.raise_for_status = MagicMock()

        with patch.object(audit_log_info_module, "requests") as mock_requests:
            mock_requests.get.return_value = mock_response
            mock_requests.RequestException = Exception

            with pytest.raises(SystemExit) as exc_info:
                audit_log_info_module.main()
            assert exc_info.value.code == 0
            mock_requests.get.assert_called_once()

    def test_api_error_fails(self):
        with patch.object(audit_log_info_module, "requests") as mock_requests:
            mock_requests.get.side_effect = Exception("connection refused")
            mock_requests.RequestException = Exception

            with pytest.raises(SystemExit) as exc_info:
                audit_log_info_module.main()
            assert exc_info.value.code == 1
