import boto3

from django.conf import settings
from celery.decorators import task

from benchmark.utils.shortcuts import get_object_or_none


@task(name="do_upload_release")
def do_upload_release(reportupload_id):
    from benchmark.report.models import ReportUpload

    report_upload = get_object_or_none(ReportUpload, pk=reportupload_id)

    if not report_upload:
        raise AttributeError('Can not determine upload')

    try:
        report_upload.do_release_tasks()
    except Exception as e:
        # TODO: Might be usefull to save information about failed release, rather than allowing to do the same twice
        report_upload.period.release.delete()
        raise e
