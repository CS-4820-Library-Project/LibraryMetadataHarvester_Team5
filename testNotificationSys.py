import unittest
from unittest.mock import patch
from notificationSys import NotificationSystem
from outputSys import LMHDataOutputSystem

class TestLMHDataOutputSystem(unittest.TestCase):
    def test_handle_error(self):
        notification_system = NotificationSystem()
        lmh_output_system = LMHDataOutputSystem()

        with patch.object(notification_system, 'notify_user') as mock_notify_user:
            lmh_output_system.handle_error("Test error message")
            mock_notify_user.assert_called_once_with("Test error message")

if __name__ == '__main__':
    unittest.main()
