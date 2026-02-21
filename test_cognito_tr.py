# -*- coding: utf-8 -*-
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

class TestCognitoTR(unittest.TestCase):
    def setUp(self):
        # Patch __init__ to avoid UI setup
        self.init_patcher = patch('cognito.CognitoWindow.__init__', return_value=None)
        self.mock_init = self.init_patcher.start()
        self.window = CognitoWindow()
        # Setup necessary attributes for tr
        self.window.translations = {
            'HELLO': {'en': 'Hello', 'ko': '안녕하세요'},
            'ONLY_EN': {'en': 'English Only'},
            'ONLY_KO': {'ko': '한국어만'},
            'PARTIAL': {'fr': 'Bonjour'}
        }
        self.window.language = 'en'

    def tearDown(self):
        self.init_patcher.stop()

    def test_tr_found_language(self):
        """Test translation when the key exists for the current language."""
        self.window.language = 'en'
        self.assertEqual(self.window.tr('HELLO'), 'Hello')

        self.window.language = 'ko'
        self.assertEqual(self.window.tr('HELLO'), '안녕하세요')

    def test_tr_fallback_to_english(self):
        """Test fallback to English when the current language translation is missing."""
        self.window.language = 'ko'
        self.assertEqual(self.window.tr('ONLY_EN'), 'English Only')

    def test_tr_fallback_key_not_in_english(self):
        """Test fallback to [key] when the current language and English are missing."""
        self.window.language = 'en'
        self.assertEqual(self.window.tr('ONLY_KO'), '[ONLY_KO]')

        self.window.language = 'fr' # Language not in dict for this key
        self.assertEqual(self.window.tr('ONLY_KO'), '[ONLY_KO]')

    def test_tr_key_missing(self):
        """Test behavior when the key is completely missing from translations."""
        self.assertEqual(self.window.tr('MISSING_KEY'), '[MISSING_KEY]')

    def test_tr_default_fallback_value(self):
        """Test that the fallback format is consistently [key]."""
        self.window.language = 'es' # Some random language
        self.assertEqual(self.window.tr('HELLO'), 'Hello') # Should fallback to en
        self.assertEqual(self.window.tr('PARTIAL'), '[PARTIAL]') # No en, no es -> [PARTIAL]

if __name__ == '__main__':
    unittest.main()
