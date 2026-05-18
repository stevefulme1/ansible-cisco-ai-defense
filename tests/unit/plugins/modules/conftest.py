"""Shared fixtures for stevefulme1.cisco_ai_defense unit tests."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json

import pytest

from ansible.module_utils import basic as module_utils_basic


@pytest.fixture
def module_args():
    """Base module args with API credentials."""
    return {
        "api_url": "https://api.example.com",
        "api_key": "test-api-key",
        "validate_certs": False,
    }


@pytest.fixture(autouse=True)
def mock_ansible_module(module_args, monkeypatch):
    """Inject module args into AnsibleModule."""
    monkeypatch.setattr(
        module_utils_basic, "_ANSIBLE_ARGS",
        module_utils_basic._build_module_args(module_args),
    )
