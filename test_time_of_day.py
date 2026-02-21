import sys
import unittest
from unittest.mock import MagicMock, patch
import datetime
import importlib.util

# 1. Mock PySide6 and google.generativeai BEFORE importing cognito
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

# 2. Import cognito_v0.1 using importlib due to invalid module name
spec = importlib.util.spec_from_file_location("cognito", "cognito_v0.1.py")
cognito = importlib.util.module_from_spec(spec)
sys.modules["cognito"] = cognito
try:
    spec.loader.exec_module(cognito)
except Exception as e:
    print(f"Warning: Module execution encountered an error: {e}")


class TestTimeOfDay(unittest.TestCase):

    def test_morning(self):
        # Morning: 05:00 <= time < 12:00
        # Check boundary 05:00
        with patch('cognito.datetime.datetime') as mock_dt:
            mock_dt.now.return_value.time.return_value = datetime.time(5, 0)
            self.assertEqual(cognito.get_time_of_day(), ["morning", "아침"])

        # Check mid-morning 08:30
        with patch('cognito.datetime.datetime') as mock_dt:
            mock_dt.now.return_value.time.return_value = datetime.time(8, 30)
            self.assertEqual(cognito.get_time_of_day(), ["morning", "아침"])

        # Check end of morning 11:59:59
        with patch('cognito.datetime.datetime') as mock_dt:
            mock_dt.now.return_value.time.return_value = datetime.time(11, 59, 59)
            self.assertEqual(cognito.get_time_of_day(), ["morning", "아침"])

    def test_afternoon(self):
        # Afternoon: 12:00 <= time < 17:00
        # Check boundary 12:00
        with patch('cognito.datetime.datetime') as mock_dt:
            mock_dt.now.return_value.time.return_value = datetime.time(12, 0)
            self.assertEqual(cognito.get_time_of_day(), ["afternoon", "오후"])

        # Check mid-afternoon 14:00
        with patch('cognito.datetime.datetime') as mock_dt:
            mock_dt.now.return_value.time.return_value = datetime.time(14, 0)
            self.assertEqual(cognito.get_time_of_day(), ["afternoon", "오후"])

        # Check end of afternoon 16:59:59
        with patch('cognito.datetime.datetime') as mock_dt:
            mock_dt.now.return_value.time.return_value = datetime.time(16, 59, 59)
            self.assertEqual(cognito.get_time_of_day(), ["afternoon", "오후"])

    def test_evening(self):
        # Evening: 17:00 <= time < 22:00
        # Check boundary 17:00
        with patch('cognito.datetime.datetime') as mock_dt:
            mock_dt.now.return_value.time.return_value = datetime.time(17, 0)
            self.assertEqual(cognito.get_time_of_day(), ["evening", "밤"])

        # Check mid-evening 19:30
        with patch('cognito.datetime.datetime') as mock_dt:
            mock_dt.now.return_value.time.return_value = datetime.time(19, 30)
            self.assertEqual(cognito.get_time_of_day(), ["evening", "밤"])

        # Check end of evening 21:59:59
        with patch('cognito.datetime.datetime') as mock_dt:
            mock_dt.now.return_value.time.return_value = datetime.time(21, 59, 59)
            self.assertEqual(cognito.get_time_of_day(), ["evening", "밤"])

    def test_late_night(self):
        # Late Night: 22:00 <= time OR time < 05:00
        # Check boundary 22:00
        with patch('cognito.datetime.datetime') as mock_dt:
            mock_dt.now.return_value.time.return_value = datetime.time(22, 0)
            self.assertEqual(cognito.get_time_of_day(), ["late night", "새벽"])

        # Check mid-late-night 23:59:59
        with patch('cognito.datetime.datetime') as mock_dt:
            mock_dt.now.return_value.time.return_value = datetime.time(23, 59, 59)
            self.assertEqual(cognito.get_time_of_day(), ["late night", "새벽"])

        # Check post-midnight 00:00
        with patch('cognito.datetime.datetime') as mock_dt:
            mock_dt.now.return_value.time.return_value = datetime.time(0, 0)
            self.assertEqual(cognito.get_time_of_day(), ["late night", "새벽"])

        # Check early morning 02:30
        with patch('cognito.datetime.datetime') as mock_dt:
            mock_dt.now.return_value.time.return_value = datetime.time(2, 30)
            self.assertEqual(cognito.get_time_of_day(), ["late night", "새벽"])

        # Check end of late night 04:59:59
        with patch('cognito.datetime.datetime') as mock_dt:
            mock_dt.now.return_value.time.return_value = datetime.time(4, 59, 59)
            self.assertEqual(cognito.get_time_of_day(), ["late night", "새벽"])

if __name__ == '__main__':
    unittest.main()
