import os
import uuid

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import JSONField as PostgresJSONField

from queued_storage.fields import QueuedFileField

from benchmark.utils.s3 import queued_s3storage


class BaseUUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    created = models.DateTimeField(
        auto_now_add=True,
        help_text="Date when object was created. Should be assigned automatically only."
    )
    modified = models.DateTimeField(
        auto_now=True,
        help_text="Date when object was modified. Should be assigned automatically only."
    )

    class Meta:
        abstract = True


def validate_upload_file_extension(value):
    ext = os.path.splitext(value.name)[1]

    valid_extensions = ['.csv', ]

    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')


def cvsfield_upload_to(obj, filenme):
    # Base path is settings.AWS_LOCATION
    return f'{obj.period.name_slug}/{obj.pk}.csv'


class CSVFileField(QueuedFileField):
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'storage': queued_s3storage,
            'validators': [validate_upload_file_extension, ],
            'upload_to': cvsfield_upload_to
        })

        return super().__init__(*args, **kwargs)


class JSONField(PostgresJSONField):
    pass