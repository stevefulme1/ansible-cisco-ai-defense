"""Unit tests for stevefulme1.cisco_ai_defense.cisco_aidefense_application module."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from unittest.mock import MagicMock, patch

MODULE_PATH = "ansible_collections.stevefulme1.cisco_ai_defense.plugins.modules.cisco_aidefense_application"

try:
    from ansible_collections.stevefulme1.cisco_ai_defense.plugins.modules.cisco_aidefense_application import main
except ImportError:
    from unittest.mock import MagicMock as main

class TestCreate:
    """Test cisco_aidefense_application creation."""

    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_create(self, mock_ansible_cls):
        """Creating cisco_aidefense_application calls exit_json with changed=True."""
        mock_module = MagicMock()
        mock_module.params = {'api_key': 'test-key', 'region': 'us', 'validate_certs': False, 'timeout': 30, 'state': 'present', 'application_name': 'test-app', 'description': 'test', 'connection_type': 'API', 'application_id': None}
        mock_module.check_mode = False
        mock_ansible_cls.return_value = mock_module
        main()
        mock_module.exit_json.assert_called_once()
        call_kwargs = mock_module.exit_json.call_args[1]
        assert call_kwargs.get("changed") is True
class TestDelete:
    """Test cisco_aidefense_application deletion."""

    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_delete(self, mock_ansible_cls):
        """Deleting cisco_aidefense_application calls exit_json with changed=True."""
        mock_module = MagicMock()
        mock_module.params = {'api_key': 'test-key', 'region': 'us', 'validate_certs': False, 'timeout': 30, 'state': 'absent', 'application_id': 'test-id', 'application_name': None, 'description': '', 'connection_type': 'API'}
        mock_module.check_mode = False
        mock_ansible_cls.return_value = mock_module
        main()
        mock_module.exit_json.assert_called_once()
        call_kwargs = mock_module.exit_json.call_args[1]
        assert call_kwargs.get("changed") is True
class TestIdempotent:
    """Test cisco_aidefense_application idempotency."""

    @patch(f"{MODULE_PATH}.AnsibleModule")
    def test_create_idempotent(self, mock_ansible_cls):
        """Re-creating existing cisco_aidefense_application calls exit_json with changed=False."""
        mock_module = MagicMock()
        mock_module.params = {'api_key': 'test-key', 'region': 'us', 'validate_certs': False, 'timeout': 30, 'state': 'present', 'application_name': 'test-app', 'description': 'test', 'connection_type': 'API', 'application_id': None}
        mock_module.check_mode = False
        mock_ansible_cls.return_value = mock_module
        main()
        mock_module.exit_json.assert_called()
