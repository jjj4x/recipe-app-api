from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class CommandTest(TestCase):
    """Test commands."""

    def test_wait_for_db_ready(self):
        """Test waiting for db until is's available."""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            connection = MagicMock()
            gi.return_value = connection

            call_command('wait_for_db')

            self.assertEqual(gi.call_count, 1)
            self.assertEqual(connection.cursor.call_count, 1)

    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, ts):
        """Test waiting for db."""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            connection = MagicMock()

            gi.side_effect = [
                OperationalError,
                OperationalError,
                OperationalError,
                OperationalError,
                OperationalError,
                connection,
            ]

            call_command('wait_for_db')

            self.assertEqual(gi.call_count, 6)
            self.assertEqual(connection.cursor.call_count, 1)
