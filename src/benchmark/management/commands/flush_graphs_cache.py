from django.core.management.base import BaseCommand

from chart import RELEASE_CACHE as cache
from chart import GRAPH_IMPLEMENTED as graphs


class Command(BaseCommand):
    help = (
        'Flush the cache for all graphs'
    )

    def handle(self, *args, **kwargs):
        for graph in graphs:
            deleted = cache.delete_pattern(f'*{graph}-*')
            self.stdout.write(f"{graph} processed, {deleted} cache objects removed\n")

        return
