"""Unit tests for stevefulme1.cisco_ai_defense.cisco_aidefense_inspect module."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from unittest.mock import MagicMock, patch

MODULE_PATH = "ansible_collections.stevefulme1.cisco_ai_defense.plugins.modules.cisco_aidefense_inspect"

try:
    from ansible_collections.stevefulme1.cisco_ai_defense.plugins.modules.cisco_aidefense_inspect import main
except ImportError:
    from unittest.mock import MagicMock as main

class TestAction:
    """Test cisco_aidefense_inspect action execution."""

    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_execute(self, mock_ansible_cls):
        """Executing cisco_aidefense_inspect returns a result."""
        mock_module = MagicMock()
        mock_module.params = {'api_key': 'test-key', 'region': 'us', 'validate_certs': False, 'timeout': 30, 'messages': [{'role': 'user', 'content': 'test'}], 'metadata': None, 'inspection_config': None}
        mock_module.check_mode = False
        mock_ansible_cls.return_value = mock_module
        main()
        mock_module.exit_json.assert_called_once()
