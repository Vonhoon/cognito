import sys
import unittest
from unittest.mock import MagicMock, patch
import importlib.util

# 1. Mock PySide6 and google.generativeai
mock_pyside6 = MagicMock()

# Define real classes for base classes to avoid Mock-inheritance issues
class MockQMainWindow: pass
class MockQDialog: pass
class MockQWidget: pass

mock_pyside6.QtWidgets.QMainWindow = MockQMainWindow
mock_pyside6.QtWidgets.QDialog = MockQDialog
mock_pyside6.QtWidgets.QWidget = MockQWidget

sys.modules['PySide6'] = mock_pyside6
sys.modules['PySide6.QtWidgets'] = mock_pyside6.QtWidgets
sys.modules['PySide6.QtCore'] = mock_pyside6.QtCore
sys.modules['PySide6.QtGui'] = mock_pyside6.QtGui
sys.modules['PySide6.QtMultimedia'] = mock_pyside6.QtMultimedia

mock_genai = MagicMock()
sys.modules['google.generativeai'] = mock_genai

# 2. Import cognito_v0.1.py
spec = importlib.util.spec_from_file_location("cognito", "cognito_v0.1.py")
cognito = importlib.util.module_from_spec(spec)
sys.modules["cognito"] = cognito
try:
    spec.loader.exec_module(cognito)
except Exception as e:
    print(f"Warning: Module execution encountered an error: {e}")

from cognito import CognitoWindow

class TestToggleMCP(unittest.TestCase):
    def setUp(self):
        # Create a mock instance of CognitoWindow
        self.win = MagicMock()
        self.win.internet_enabled = False
        self.win.mcp_enabled = False
        self.win.game_state = "NORMAL_NO_PERMISSIONS"
        self.win.pending_prompt = None
        self.win.language = 'en'
        self.win.internet_button = MagicMock()
        self.win.mcp_button = MagicMock()
        self.win.statusBar = MagicMock()

        # We need to make sure tr returns something
        self.win.tr.side_effect = lambda x: x

    def test_mcp_button_disabled(self):
        # Setup: button is disabled, mcp is off
        self.win.mcp_button.isEnabled.return_value = False
        self.win.mcp_enabled = False

        # Action
        CognitoWindow.toggle_mcp(self.win)

        # Verification: mcp_enabled remains False
        self.assertFalse(self.win.mcp_enabled)
        # Style update should NOT be called
        self.win._update_button_style.assert_not_called()

    def test_toggle_mcp_off_to_on(self):
        # Setup: button is enabled, mcp is off
        self.win.mcp_button.isEnabled.return_value = True
        self.win.mcp_enabled = False
        self.win.game_state = "NORMAL_INTERNET_ONLY"

        # Action
        CognitoWindow.toggle_mcp(self.win)

        # Verification
        self.assertTrue(self.win.mcp_enabled)
        self.win._update_button_style.assert_called_with(self.win.mcp_button, True)
        self.win.statusBar.showMessage.assert_called_with('STATUS_MCP_ENABLED', 3000)
        self.win.flash_effect.assert_called_once()

    def test_toggle_mcp_on_to_off(self):
        # Setup: button is enabled, mcp is on, state is ALL_PERMISSIONS
        self.win.mcp_button.isEnabled.return_value = True
        self.win.mcp_enabled = True
        self.win.game_state = "NORMAL_ALL_PERMISSIONS"

        # Action
        CognitoWindow.toggle_mcp(self.win)

        # Verification
        self.assertFalse(self.win.mcp_enabled)
        self.win._update_button_style.assert_called_with(self.win.mcp_button, False)
        self.win.statusBar.showMessage.assert_called_with('STATUS_MCP_REVOKED', 3000)
        # Verify state reverts to NORMAL_INTERNET_ONLY
        self.assertEqual(self.win.game_state, "NORMAL_INTERNET_ONLY")

    def test_mcp_awaiting_confirm(self):
        # Setup: awaiting MCP confirm, enabling it
        self.win.mcp_button.isEnabled.return_value = True
        self.win.mcp_enabled = False
        self.win.game_state = "AWAITING_MCP_CONFIRM"
        self.win.generate_aura_response.return_value = "Response from Aura"

        # Action
        CognitoWindow.toggle_mcp(self.win)

        # Verification
        self.win.generate_aura_response.assert_called_with(
            "User enabled MCP access",
            internal_trigger=True,
            trigger_context="mcp_enabled"
        )
        self.win.display_aura_message.assert_called_with("Response from Aura")

if __name__ == '__main__':
    unittest.main()
