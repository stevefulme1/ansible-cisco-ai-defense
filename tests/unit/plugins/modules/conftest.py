"""Shared fixtures for stevefulme1.cisco_ai_defense unit tests."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import importlib
import os
import sys
import types
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# Bootstrap: make the collection importable without pip-installing it.
#
# Modules use two styles:
#   OLD: ``import requests`` at module level (policy, guardrail, policy_info,
#        audit_log_info).
#   NEW: ``from ansible_collections.stevefulme1.cisco_ai_defense
#              .plugins.module_utils.ai_defense import AiDefenseClient``
#
# For NEW modules the namespace ``ansible_collections.stevefulme1...`` must
# exist in ``sys.modules`` *before* ``importlib.import_module`` loads the
# module, otherwise Python raises ``ModuleNotFoundError``.
#
# We solve this by:
#   1. Adding plugins/modules and plugins/module_utils to sys.path.
#   2. Importing the real ``ai_defense`` module from module_utils.
#   3. Injecting it (and all its parent packages) into sys.modules under the
#      fully-qualified collection namespace so that ``from ansible_collections
#      .stevefulme1...`` resolves at import time.
# ---------------------------------------------------------------------------

_REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
)
_MODULES_DIR = os.path.join(_REPO_ROOT, "plugins", "modules")
_MODULE_UTILS_DIR = os.path.join(_REPO_ROOT, "plugins", "module_utils")

# Ensure both directories are importable
for _p in (_MODULES_DIR, _MODULE_UTILS_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Import the real ai_defense helper so AiDefenseClient is available
_ai_defense_mod = importlib.import_module("ai_defense")

# Build the namespace chain:
# ansible_collections.stevefulme1.cisco_ai_defense.plugins.module_utils.ai_defense
_ns_parts = [
    "ansible_collections",
    "ansible_collections.stevefulme1",
    "ansible_collections.stevefulme1.cisco_ai_defense",
    "ansible_collections.stevefulme1.cisco_ai_defense.plugins",
    "ansible_collections.stevefulme1.cisco_ai_defense.plugins.module_utils",
    "ansible_collections.stevefulme1.cisco_ai_defense.plugins.module_utils.ai_defense",
]

for _part in _ns_parts:
    if _part not in sys.modules:
        if _part == _ns_parts[-1]:
            # The leaf is the real module
            sys.modules[_part] = _ai_defense_mod
        else:
            # Intermediate packages are simple namespace stubs
            _pkg = types.ModuleType(_part)
            _pkg.__path__ = []
            _pkg.__package__ = _part
            sys.modules[_part] = _pkg


def set_module_args(args):
    """Prepare module args for AnsibleModule.

    Works with Ansible 2.21+ which requires _ANSIBLE_PROFILE alongside
    _ANSIBLE_ARGS.
    """
    import json
    from ansible.module_utils import basic as module_utils_basic

    module_utils_basic._ANSIBLE_ARGS = json.dumps(
        {"ANSIBLE_MODULE_ARGS": args}
    ).encode("utf-8")
    module_utils_basic._ANSIBLE_PROFILE = "legacy"


@pytest.fixture
def module_args():
    """Base module args with API credentials."""
    return {
        "api_url": "https://api.example.com",
        "api_key": "test-api-key",
        "validate_certs": False,
    }


@pytest.fixture
def mock_client():
    """Return a pre-configured MagicMock of AiDefenseClient."""
    client = MagicMock()
    client.get.return_value = None
    client.post.return_value = {}
    client.put.return_value = {}
    client.delete.return_value = None
    return client
