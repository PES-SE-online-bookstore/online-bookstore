"""Report whether this Django process's PostgreSQL connection uses TLS."""

from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    help = "Verify TLS on the current PostgreSQL connection without printing credentials."

    def handle(self, *args, **options):
        if connection.vendor != "postgresql":
            raise CommandError("The default database is not PostgreSQL.")

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT ssl, version, cipher "
                "FROM pg_stat_ssl "
                "WHERE pid = pg_backend_pid()"
            )
            row = cursor.fetchone()

        if not row:
            raise CommandError("PostgreSQL did not report TLS status for this connection.")

        ssl_enabled, version, cipher = row
        if not ssl_enabled:
            raise CommandError("The current PostgreSQL connection is not using TLS.")

        self.stdout.write(
            self.style.SUCCESS(f"TLS is active: {version}; cipher: {cipher}")
        )
