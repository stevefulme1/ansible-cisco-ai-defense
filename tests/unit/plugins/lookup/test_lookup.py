"""Unit tests for stevefulme1.cisco_ai_defense.ai_defense_policy lookup plugin."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import importlib
import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

from ansible.errors import AnsibleError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'plugins', 'lookup'))
lookup_module = importlib.import_module('ai_defense_policy')
LookupModule = lookup_module.LookupModule


class TestLookupModule:
    """Tests for the ai_defense_policy lookup plugin."""

    @pytest.fixture
    def lookup(self):
        inst = LookupModule()
        return inst

    def _make_options(self, **kwargs):
        """Return a get_option mock backed by a dict."""
        defaults = {
            "api_url": "https://api.example.com/api/v1",
            "api_key": "test-key",
            "validate_certs": True,
            "organization_id": None,
        }
        defaults.update(kwargs)
        return defaults

    @patch.object(LookupModule, "_fetch_policy")
    def test_single_term_returns_list(self, mock_fetch, lookup):
        mock_fetch.return_value = {"id": "pol-1", "name": "my-policy", "enabled": True}
        opts = self._make_options()
        lookup.set_options = MagicMock()
        lookup.get_option = MagicMock(side_effect=lambda k: opts[k])

        result = lookup.run(["my-policy"], variables={})

        assert len(result) == 1
        assert result[0]["name"] == "my-policy"

    @patch.object(LookupModule, "_fetch_policy")
    def test_multiple_terms(self, mock_fetch, lookup):
        mock_fetch.side_effect = [
            {"id": "pol-1", "name": "policy-1"},
            {"id": "pol-2", "name": "policy-2"},
        ]
        opts = self._make_options()
        lookup.set_options = MagicMock()
        lookup.get_option = MagicMock(side_effect=lambda k: opts[k])

        result = lookup.run(["policy-1", "policy-2"], variables={})

        assert len(result) == 2
        assert mock_fetch.call_count == 2

    @patch.object(LookupModule, "_fetch_policy")
    def test_fetch_failure_raises_ansible_error(self, mock_fetch, lookup):
        mock_fetch.side_effect = Exception("connection refused")
        opts = self._make_options()
        lookup.set_options = MagicMock()
        lookup.get_option = MagicMock(side_effect=lambda k: opts[k])

        with pytest.raises(AnsibleError, match="Failed to look up policy"):
            lookup.run(["bad-policy"], variables={})

    def test_missing_api_key_raises_error(self, lookup):
        opts = self._make_options(api_key=None)
        lookup.set_options = MagicMock()
        lookup.get_option = MagicMock(side_effect=lambda k: opts[k])

        with pytest.raises(AnsibleError, match="API key is required"):
            lookup.run(["test"], variables={})

    @patch.object(lookup_module, "open_url")
    def test_fetch_policy_constructs_url(self, mock_open_url):
        response = MagicMock()
        response.read.return_value = json.dumps({"id": "p1"}).encode()
        mock_open_url.return_value = response

        result = LookupModule._fetch_policy(
            api_url="https://api.example.com/api/v1",
            api_key="test-key",
            validate_certs=True,
            organization_id=None,
            policy_identifier="my-policy",
        )

        assert result["id"] == "p1"
        call_url = mock_open_url.call_args[0][0]
        assert call_url == "https://api.example.com/api/v1/policies/my-policy"

    @patch.object(lookup_module, "open_url")
    def test_fetch_policy_with_org_id(self, mock_open_url):
        response = MagicMock()
        response.read.return_value = json.dumps({"id": "p1"}).encode()
        mock_open_url.return_value = response

        LookupModule._fetch_policy(
            api_url="https://api.example.com/api/v1",
            api_key="test-key",
            validate_certs=True,
            organization_id="org-123",
            policy_identifier="my-policy",
        )

        call_url = mock_open_url.call_args[0][0]
        assert "organizations/org-123" in call_url

    @patch.object(lookup_module, "open_url")
    def test_fetch_policy_api_error(self, mock_open_url):
        mock_open_url.side_effect = Exception("404 Not Found")

        with pytest.raises(AnsibleError, match="API request"):
            LookupModule._fetch_policy(
                api_url="https://api.example.com/api/v1",
                api_key="test-key",
                validate_certs=True,
                organization_id=None,
                policy_identifier="missing",
            )
