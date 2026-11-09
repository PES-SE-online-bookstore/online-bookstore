from io import StringIO
from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase


class VerifyPostgresTlsCommandTests(SimpleTestCase):
    """Unit tests of the verifier with the DB connection mocked.

    They prove the command's reporting logic only. Actual Render PostgreSQL TLS
    requires running `manage.py verify_postgres_tls` on the deployed service.
    """

    qa_level = "Unit"
    qa_requirements = ("BOOK-SR-001",)

    @patch("accounts.management.commands.verify_postgres_tls.connection")
    def test_reports_tls_version_and_cipher(self, connection):
        connection.vendor = "postgresql"
        cursor = MagicMock()
        cursor.fetchone.return_value = (True, "TLSv1.3", "TLS_AES_256_GCM_SHA384")
        connection.cursor.return_value.__enter__.return_value = cursor
        output = StringIO()

        call_command("verify_postgres_tls", stdout=output)

        self.assertIn("TLS is active: TLSv1.3", output.getvalue())
        self.assertIn("TLS_AES_256_GCM_SHA384", output.getvalue())
        cursor.execute.assert_called_once()

    @patch("accounts.management.commands.verify_postgres_tls.connection")
    def test_fails_when_connection_is_not_encrypted(self, connection):
        connection.vendor = "postgresql"
        cursor = MagicMock()
        cursor.fetchone.return_value = (False, None, None)
        connection.cursor.return_value.__enter__.return_value = cursor

        with self.assertRaisesMessage(CommandError, "not using TLS"):
            call_command("verify_postgres_tls")

    @patch("accounts.management.commands.verify_postgres_tls.connection")
    def test_rejects_non_postgresql_database(self, connection):
        connection.vendor = "sqlite"

        with self.assertRaisesMessage(CommandError, "not PostgreSQL"):
            call_command("verify_postgres_tls")
