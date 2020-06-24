from time import sleep

from django.db import OperationalError, connections
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Pause the execution until the db is available."""

    def add_arguments(self, parser):
        parser.add_argument(
            '--retry',
            default=7,
            type=int,
            help='Retry attempts counter.',
        )

    def handle(self, *args, **options):
        retry = options['retry']

        self.stdout.write(f'Waiting for db up to {retry} max tries...')

        result = None
        while not result and retry:
            retry -= 1

            try:
                with connections['default'].cursor() as cursor:
                    cursor.execute('select 1')
                    result = cursor.fetchone()
            except OperationalError:
                self.stdout.write('Waiting for 1 second...')
                sleep(1)

        if result:
            self.stdout.write(self.style.SUCCESS('Database is available.'))
            return

        self.stdout.write(self.style.ERROR('Cannot connect to the database.'))
        exit(1)
