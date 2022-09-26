from django.core.management.base import BaseCommand

from ._run_bot import run_bot


class Command(BaseCommand):
    help = 'start tg bot'

    def handle(self, *args, **options):
        run_bot()
