import sys
import unittest
from unittest.mock import MagicMock, patch, mock_open
import importlib.util
import builtins
import os

# 1. Mock PySide6 and google.generativeai
mock_pyside6 = MagicMock()
class MockQMainWindow: pass
class MockQDialog: pass
class MockQWidget: pass
mock_pyside6.QtWidgets.QMainWindow = MockQMainWindow
mock_pyside6.QtWidgets.QDialog = MockQDialog
mock_pyside6.QtWidgets.QWidget = MockQWidget

# Mock crucial parts
mock_pyside6.QtWidgets.QApplication.instance = MagicMock()
mock_pyside6.QtWidgets.QInputDialog = MagicMock()
mock_pyside6.QtWidgets.QInputDialog.getText = MagicMock(return_value=('secret_key', True))
mock_pyside6.QtWidgets.QLineEdit = MagicMock()
mock_pyside6.QtWidgets.QLineEdit.EchoMode = MagicMock()
mock_pyside6.QtWidgets.QLineEdit.EchoMode.Password = MagicMock()

sys.modules['PySide6'] = mock_pyside6
sys.modules['PySide6.QtWidgets'] = mock_pyside6.QtWidgets
sys.modules['PySide6.QtCore'] = mock_pyside6.QtCore
sys.modules['PySide6.QtGui'] = mock_pyside6.QtGui
sys.modules['PySide6.QtMultimedia'] = mock_pyside6.QtMultimedia

# Mock google and google.generativeai properly
mock_google = MagicMock()
sys.modules['google'] = mock_google
mock_genai = MagicMock()
sys.modules['google.generativeai'] = mock_genai
mock_google.generativeai = mock_genai

# 2. Import cognito_v0.1.py
# If 'cognito' is already in sys.modules, reloading via importlib might be tricky if getpass is added later.
# We'll rely on reloading it in the test or assuming this script runs once per modification cycle.
if "cognito" in sys.modules:
    del sys.modules["cognito"]

spec = importlib.util.spec_from_file_location("cognito", "cognito_v0.1.py")
cognito = importlib.util.module_from_spec(spec)
sys.modules["cognito"] = cognito
# We execute the module later or now? Now is fine.
spec.loader.exec_module(cognito)

if not cognito.GOOGLE_AI_AVAILABLE:
    print("Forcing GOOGLE_AI_AVAILABLE to True for test.")
    cognito.GOOGLE_AI_AVAILABLE = True

# We need to ensure getpass is mocked correctly if it's imported inside the module or used via import
# Since we will modify the module to import getpass, we should patch it in the test method or setup.

class TestSecurityFix(unittest.TestCase):
    def setUp(self):
        self.win = MagicMock()
        self.win.tr.side_effect = lambda x: x
        # Bind the original method to our mock instance
        # Re-fetch the method from the module in case it was reloaded
        self.win.setup_llm_client = cognito.CognitoWindow.setup_llm_client.__get__(self.win, cognito.CognitoWindow)

    @patch('builtins.input', return_value='insecure_key')
    @patch('getpass.getpass', return_value='secure_console_key')
    @patch('builtins.open', new_callable=mock_open)
    def test_console_fallback(self, mock_file, mock_getpass, mock_input):
        # Scenario: Console mode (QApplication.instance() returns None)
        mock_pyside6.QtWidgets.QApplication.instance.return_value = None
        mock_file.side_effect = FileNotFoundError

        print("\nRunning test_console_fallback...")
        self.win.setup_llm_client()

        # Verify getpass was called
        # Note: Before the fix, this will fail because getpass is not called.
        try:
            mock_getpass.assert_called_once()
            print("PASS: getpass used in console mode.")
        except AssertionError:
            print("FAIL: getpass NOT used.")
            raise

        # Verify input was NOT called
        try:
            mock_input.assert_not_called()
            print("PASS: input() skipped.")
        except AssertionError:
            print("FAIL: input() WAS called.")
            raise

    @patch('builtins.input', return_value='insecure_key')
    @patch('getpass.getpass', return_value='secure_console_key')
    @patch('builtins.open', new_callable=mock_open)
    def test_gui_dialog(self, mock_file, mock_getpass, mock_input):
        # Scenario: GUI mode (QApplication.instance() returns an object)
        mock_pyside6.QtWidgets.QApplication.instance.return_value = MagicMock()
        mock_file.side_effect = FileNotFoundError

        # Set return value for QInputDialog
        mock_pyside6.QtWidgets.QInputDialog.getText.return_value = ('secure_gui_key', True)

        print("\nRunning test_gui_dialog...")
        self.win.setup_llm_client()

        # Verify QInputDialog was used
        try:
            mock_pyside6.QtWidgets.QInputDialog.getText.assert_called_once()
            print("PASS: QInputDialog used in GUI mode.")
        except AssertionError:
            print("FAIL: QInputDialog NOT used.")
            raise

        # Verify input was NOT called
        try:
            mock_input.assert_not_called()
            print("PASS: input() skipped.")
        except AssertionError:
            print("FAIL: input() WAS called.")
            raise

if __name__ == '__main__':
    unittest.main()
