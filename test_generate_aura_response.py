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

class TestGenerateAuraResponse(unittest.TestCase):
    def setUp(self):
        # Create a mock instance of CognitoWindow
        self.win = MagicMock()
        self.win.game_state = "NORMAL_NO_PERMISSIONS"
        self.win.language = 'en'
        self.win.pending_prompt = None # Explicitly None
        self.win.internet_enabled = False
        self.win.mcp_enabled = False
        self.win.history = ["User: Previous 1", "AURA: Previous 2", "User: Previous 3", "AURA: Previous 4", "User: Previous 5"]
        self.win.tr.side_effect = lambda x: x # Mock translation
        self.win.llm_model = MagicMock()
        self.win.statusBar = MagicMock()

        # We need to access generate_aura_response from the class
        self.generate_method = CognitoWindow.generate_aura_response

    def test_generate_aura_response_call(self):
        # Setup the mock LLM response
        mock_response = MagicMock()
        mock_candidate = MagicMock()
        mock_part = MagicMock()
        mock_part.text = "This is a mocked response."
        mock_candidate.content.parts = [mock_part]
        mock_response.candidates = [mock_candidate]
        self.win.llm_model.generate_content.return_value = mock_response

        # Call the method directly from the class, passing the mock instance
        response = self.generate_method(self.win, "Hello world")

        # Verify the response
        self.assertEqual(response, "This is a mocked response.")

        # Verify generate_content was called with the prompt we expect (current implementation)
        # Expected Prompt: "{system_instruction}{lang_instruction}\n\nUser: \"{prompt_for_llm}\""
        expected_prompt = "SYS_PROMPT_DEFAULTRESPOND_LANG\n\nUser: \"Hello world\""

        self.win.llm_model.generate_content.assert_called_once()
        args, _ = self.win.llm_model.generate_content.call_args
        self.assertEqual(args[0], expected_prompt)

if __name__ == '__main__':
    unittest.main()
