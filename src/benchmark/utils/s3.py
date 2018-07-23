from django.conf import settings

from queued_storage.backends import QueuedStorage
from storages.backends.s3boto3 import S3Boto3Storage


queued_s3storage = QueuedStorage(
    'django.core.files.storage.FileSystemStorage',
    'storages.backends.s3boto3.S3Boto3Storage',
    remote_options={'location': settings.AWS_UPLOADS_LOCATION}
)


MediaS3BotoStorage = lambda: S3Boto3Storage(location=settings.APPDATA_PREFIX)
