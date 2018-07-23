from django.core.management.base import BaseCommand

from benchmark.report.models import ReportRelease
from benchmark.report.tasks import do_upload_release


class Command(BaseCommand):
    help = (
        'Rebuild the release cache per release'
    )

    def handle(self, *args, **kwargs):
        for release in ReportRelease.objects.all():
            if release:
                try:
                    do_upload_release.delay(reportupload_id=release.report_id)

                    self.stdout.write(f"Completed, rebuild cache for {release.report.name}\n")
                except Exception as e:
                    raise e

        return
