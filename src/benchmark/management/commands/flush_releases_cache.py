from django.core.management.base import BaseCommand

from chart import RELEASE_CACHE as cache


class Command(BaseCommand):
    help = (
        'Flush the whole releases cache'
    )

    def handle(self, *args, **kwargs):
        deleted = cache.delete_pattern(f'*')

        self.stdout.write(f"Done, {deleted} cache objects removed\n")

        return
