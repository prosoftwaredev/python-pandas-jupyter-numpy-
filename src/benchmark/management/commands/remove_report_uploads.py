from django.core.management.base import BaseCommand

from benchmark.report.models import ReportUpload, ReportRelease


class Command(BaseCommand):
    help = (
        'Clean report app data - remove all report uploads and releases'
    )

    def handle(self, *args, **kwargs):
        total_affected, results = ReportUpload.objects.all().delete()

        self.stdout.write(f"Completed, {total_affected} objects removed\n")

        return
