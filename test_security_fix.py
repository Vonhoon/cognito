
import sys
import unittest
from unittest.mock import MagicMock, patch
import importlib.util
import os

# --- MOCKING ---
# We must mock PySide6 modules BEFORE importing the application code.
# The application does: from PySide6 import QtWidgets, QtCore, QtGui
# And: from PySide6.QtMultimedia import QSoundEffect

# Create mock modules
mock_pyside6 = MagicMock()
# Ensure PySide6 acts as a package
mock_pyside6.__path__ = []

mock_qtwidgets = MagicMock()
mock_qtcore = MagicMock()
mock_qtgui = MagicMock()
mock_qtmultimedia = MagicMock()
mock_google = MagicMock()
mock_genai = MagicMock()

# Link the submodules to the parent package mock to ensure consistency
mock_pyside6.QtWidgets = mock_qtwidgets
mock_pyside6.QtCore = mock_qtcore
mock_pyside6.QtGui = mock_qtgui
mock_pyside6.QtMultimedia = mock_qtmultimedia

# Configure specific classes needed for inheritance
class MockQMainWindow:
    def __init__(self, *args, **kwargs): pass
    def setWindowTitle(self, title): pass
    def setStyleSheet(self, style): pass
    def setCentralWidget(self, widget): pass
    def addDockWidget(self, area, dock): pass
    def setStatusBar(self, statusbar): pass
    def showFullScreen(self): pass
    def setFont(self, font): pass
    def pos(self): return MagicMock()
    def move(self, pos): pass
    def close(self): pass
    def tr(self, text): return text
    def show(self): pass
    def hide(self): pass
    def isFullScreen(self): return False
    def showNormal(self): pass
    def rect(self): return MagicMock()
    def resizeEvent(self, event): pass
    def keyPressEvent(self, event): pass

class MockQDialog:
    def __init__(self, parent=None): pass
    def exec(self): return 1 # Accepted
    def setWindowTitle(self, title): pass
    def setStyleSheet(self, style): pass
    def setMinimumWidth(self, width): pass
    def accept(self): pass

class MockQWidget:
    def __init__(self, parent=None): pass
    def setStyleSheet(self, style): pass
    def setContextMenuPolicy(self, policy): pass
    def customContextMenuRequested(self, signal): pass
    def rect(self): return MagicMock()
    def hide(self): pass
    def show(self): pass
    def raise_(self): pass
    def setGeometry(self, rect): pass
    def setLayout(self, layout): pass
    def mapToGlobal(self, pos): return pos

class MockQTimer:
    def __init__(self, parent=None):
        self.timeout = MagicMock()
        self.timeout.connect = MagicMock()
    def start(self, interval): pass
    def stop(self): pass
    def isActive(self): return False
    @staticmethod
    def singleShot(interval, callback):
        # For testing purposes, we might want to execute immediately or ignore
        pass

# Assign mocks to sys.modules
sys.modules['PySide6'] = mock_pyside6
sys.modules['PySide6.QtWidgets'] = mock_qtwidgets
sys.modules['PySide6.QtCore'] = mock_qtcore
sys.modules['PySide6.QtGui'] = mock_qtgui
sys.modules['PySide6.QtMultimedia'] = mock_qtmultimedia
sys.modules['google'] = mock_google
sys.modules['google.generativeai'] = mock_genai

# Assign classes to the mocked modules
mock_qtwidgets.QMainWindow = MockQMainWindow
mock_qtwidgets.QDialog = MockQDialog
mock_qtwidgets.QWidget = MockQWidget
mock_qtwidgets.QApplication = MagicMock()
mock_qtwidgets.QTextEdit = MagicMock()
mock_qtwidgets.QLineEdit = MagicMock()
mock_qtwidgets.QPushButton = MagicMock()
mock_qtwidgets.QLabel = MagicMock()
mock_qtwidgets.QVBoxLayout = MagicMock()
mock_qtwidgets.QHBoxLayout = MagicMock()
mock_qtwidgets.QMessageBox = MagicMock()
mock_qtwidgets.QDockWidget = MagicMock()
mock_qtwidgets.QStatusBar = MagicMock()
mock_qtwidgets.QMenu = MagicMock()

mock_qtcore.QTimer = MockQTimer
mock_qtcore.QUrl = MagicMock()
mock_qtcore.Qt = MagicMock()

mock_qtgui.QFont = MagicMock()
mock_qtgui.QFontDatabase = MagicMock()
mock_qtgui.QTextCursor = MagicMock()

mock_qtmultimedia.QSoundEffect = MagicMock()

# Setup QFontDatabase return values
mock_qtgui.QFontDatabase.addApplicationFont.return_value = 0
mock_qtgui.QFontDatabase.applicationFontFamilies.return_value = ["MockFont"]


# Import the module using importlib because of the filename
spec = importlib.util.spec_from_file_location("cognito_v0_1", "cognito_v0.1.py")
cognito_v0_1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cognito_v0_1)

print(f"DEBUG: cognito_v0_1.CognitoWindow type: {type(cognito_v0_1.CognitoWindow)}")
print(f"DEBUG: cognito_v0_1.CognitoWindow dir: {dir(cognito_v0_1.CognitoWindow)}")

# --- TESTS ---

class TestSecurityIssue(unittest.TestCase):
    def test_sensitive_log_exposure(self):
        # We need to mock methods that interact with UI to prevent errors
        with patch.object(cognito_v0_1.CognitoWindow, 'setup_ui'), \
             patch.object(cognito_v0_1.CognitoWindow, 'setup_sounds'), \
             patch.object(cognito_v0_1.CognitoWindow, 'display_top'), \
             patch.object(cognito_v0_1.CognitoWindow, 'showFullScreen'), \
             patch.object(cognito_v0_1.CognitoWindow, 'setup_llm_client'), \
             patch.object(cognito_v0_1.CognitoWindow, 'tr', side_effect=lambda x: x), \
             patch('builtins.print') as mock_print: # Mock print globally to verify calls

            # Instantiate the window
            window = cognito_v0_1.CognitoWindow(language='en')

            # Manually set attributes that setup_ui would have set
            window.statusBar = MagicMock()
            window.statusBar.showMessage = MagicMock()

            # Setup LLM mock
            window.llm_model = MagicMock()
            mock_response = MagicMock()
            mock_candidate = MagicMock()
            mock_part = MagicMock()
            mock_part.text = "SENSITIVE_DATA_PAYLOAD_12345"
            mock_candidate.content.parts = [mock_part]
            mock_response.candidates = [mock_candidate]
            window.llm_model.generate_content.return_value = mock_response

            # Helper to set state
            window.game_state = "NORMAL_INTERNET_ONLY"
            window.mission_received = True
            window.history = [] # Initialize history list

            # Mock display_aura_message to avoid UI interaction errors
            window.display_aura_message = MagicMock()

            # Trigger the method
            window.generate_aura_response("Hello")

            # Verify that the sensitive data was printed
            # Check if any call to print contained the sensitive string
            found = False
            for call in mock_print.call_args_list:
                args, _ = call
                if args and "LLM Raw Response Text: 'SENSITIVE_DATA_PAYLOAD_12345'" in str(args[0]):
                    found = True
                    break

            self.assertFalse(found, "The sensitive LLM response text WAS found in the logs (print calls). Vulnerability still exists!")

            # Also check for the safe replacement message
            found_safe = False
            for call in mock_print.call_args_list:
                args, _ = call
                if args and "LLM Response received (content hidden for security)." in str(args[0]):
                    found_safe = True
                    break
            self.assertTrue(found_safe, "The safe replacement log message was NOT found.")

if __name__ == '__main__':
    unittest.main()
