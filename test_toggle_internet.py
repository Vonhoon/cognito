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

from cognito import CognitoWindow, COMPUTATION_KEYWORDS

class TestToggleInternet(unittest.TestCase):
    def setUp(self):
        # Create a mock instance of CognitoWindow
        # We don't use spec=CognitoWindow because CognitoWindow might still be problematic to spec
        # instead we just create a MagicMock and manually ensure it has the methods we want to test.
        self.win = MagicMock()
        self.win.internet_enabled = False
        self.win.mcp_enabled = False
        self.win.game_state = "NORMAL"
        self.win.pending_prompt = None
        self.win.language = 'en'
        self.win.internet_button = MagicMock()
        self.win.mcp_button = MagicMock()
        self.win.statusBar = MagicMock()

        # We need to make sure tr returns something
        self.win.tr.side_effect = lambda x: x

    def test_toggle_off_to_on(self):
        self.win.internet_enabled = False
        # Call the actual method from the class, passing our mock instance as 'self'
        CognitoWindow.toggle_internet(self.win)

        self.assertTrue(self.win.internet_enabled)
        self.win._update_button_style.assert_called_with(self.win.internet_button, True)
        self.win.statusBar.showMessage.assert_called_with('STATUS_INTERNET_ENABLED', 3000)

    def test_toggle_on_to_off(self):
        self.win.internet_enabled = True
        self.win.mcp_enabled = True
        CognitoWindow.toggle_internet(self.win)

        self.assertFalse(self.win.internet_enabled)
        self.assertFalse(self.win.mcp_enabled)
        self.win.mcp_button.setEnabled.assert_called_with(False)
        self.win._update_button_style.assert_any_call(self.win.internet_button, False)
        self.win._update_button_style.assert_any_call(self.win.mcp_button, False)
        self.win.statusBar.showMessage.assert_called_with('STATUS_INTERNET_DISABLED', 3000)

    def test_awaiting_internet_confirm_with_computation(self):
        self.win.internet_enabled = False
        self.win.game_state = "AWAITING_INTERNET_CONFIRM"
        self.win.pending_prompt = "Please calculate the flux"
        self.win.generate_aura_response.return_value = "Response from Aura"

        CognitoWindow.toggle_internet(self.win)

        self.win.generate_aura_response.assert_called()
        self.win.display_aura_message.assert_called_with("Response from Aura")
        self.win.mcp_button.setEnabled.assert_called_with(True)
        # Verify _update_button_style was called for mcp_button
        self.win._update_button_style.assert_any_call(self.win.mcp_button, self.win.mcp_enabled)

    def test_awaiting_internet_confirm_no_computation(self):
        self.win.internet_enabled = False
        self.win.game_state = "AWAITING_INTERNET_CONFIRM"
        self.win.pending_prompt = "Hello"
        self.win.generate_aura_response.return_value = "Response from Aura"

        CognitoWindow.toggle_internet(self.win)

        self.win.generate_aura_response.assert_called()
        # mcp_button should NOT be enabled if no computation keywords
        calls = [call for call in self.win.mcp_button.setEnabled.call_args_list if call.args and call.args[0] == True]
        self.assertEqual(len(calls), 0)

    def test_normal_internet_only(self):
        self.win.internet_enabled = False
        self.win.game_state = "NORMAL_INTERNET_ONLY"

        CognitoWindow.toggle_internet(self.win)

        self.win.mcp_button.setEnabled.assert_called_with(True)
        self.win._update_button_style.assert_any_call(self.win.mcp_button, self.win.mcp_enabled)

if __name__ == '__main__':
    unittest.main()
