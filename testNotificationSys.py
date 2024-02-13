import unittest
from unittest.mock import patch
from notificationSys import NotificationSystem
from outputSys import LMHDataOutputSystem


class TestLMHDataOutputSystem(unittest.TestCase):
    def setUp(self):
        self.notification_system = NotificationSystem()
        self.lmh_output_system = LMHDataOutputSystem()
        self.lmh_output_system.notification_system = self.notification_system

    def test_handle_error(self):
        with patch.object(self.notification_system, 'notify_user') as mock_notify_user:
            self.lmh_output_system.handle_error("Test error message")
            mock_notify_user.assert_called_once_with("Test error message")

    def test_retrieve_metadata_error(self):
        with patch.object(self.notification_system, 'notify_user') as mock_notify_user:
            with patch.object(self.lmh_output_system, 'cursor') as mock_cursor:
                # Simulate an error during metadata retrieval
                mock_cursor.execute.side_effect = Exception("Test metadata retrieval error")
                metadata = self.lmh_output_system.retrieve_metadata("1234", 0)

            # Ensure that an error notification is triggered
            mock_notify_user.assert_called_once_with("Error retrieving metadata: Test metadata retrieval error")
            # Ensure that an empty metadata list is returned
            self.assertEqual(metadata, [])

    def test_is_in_database_error(self):
        with patch.object(self.notification_system, 'notify_user') as mock_notify_user:
            with patch.object(self.lmh_output_system, 'cursor') as mock_cursor:
                # Simulate an error during is_in_database check
                mock_cursor.execute.side_effect = Exception("Test database check error")
                result = self.lmh_output_system.is_in_database("1234", 0)

            # Ensure that an error notification is triggered
            mock_notify_user.assert_called_once_with("Error checking database: Test database check error")
            # Ensure that is_in_database returns False
            self.assertFalse(result)

    def test_reset_database_error(self):
        with patch.object(self.notification_system, 'notify_user') as mock_notify_user:
            with patch.object(self.lmh_output_system, 'cursor') as mock_cursor:
                # Simulate an error during database reset
                mock_cursor.execute.side_effect = Exception("Test database reset error")
                self.lmh_output_system.reset_database()

            # Ensure that an error notification is triggered
            mock_notify_user.assert_called_once_with("Error resetting database: Test database reset error")

    def test_display_database_error(self):
        with patch.object(self.notification_system, 'notify_user') as mock_notify_user:
            with patch.object(self.lmh_output_system, 'cursor') as mock_cursor:
                # Simulate an error during displaying the database
                mock_cursor.execute.side_effect = Exception("Test display database error")
                self.lmh_output_system.display_database()

            # Ensure that an error notification is triggered
            mock_notify_user.assert_called_once_with("Error displaying database: Test display database error")


if __name__ == '__main__':
    unittest.main()
