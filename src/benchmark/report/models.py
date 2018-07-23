import boto3
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.conf import settings

from chart import ReleaseManifest, ReleaseDataframe

from benchmark.account.models import Account, Agency
from benchmark.report.mixins import ReleaseManifestMixin
from benchmark.report.tasks import do_upload_release

from chart import RELEASE_CACHE as release_cache, CHART_CACHE as chart_cache
from benchmark.utils.models import BaseUUIDModel, TimeStampedModel, JSONField, CSVFileField


class ReportPeriod(BaseUUIDModel, TimeStampedModel):
    name = models.CharField(max_length=40, help_text='Name')
    financial_year = models.CharField(max_length=40, help_text='Financial year')

    csv_fields = models.CharField(max_length=1000, blank=True, help_text='CSV fields')

    start = models.DateField(help_text='Start date')
    end = models.DateField(help_text='End date')

    metadata = JSONField(null=True, blank=True, help_text='Metadata')

    class Meta:
        verbose_name = 'Report Period'
        verbose_name_plural = 'Report Periods'
        ordering = ['-created', ]

    def __str__(self):
        return self.name # name_slug

    @staticmethod
    def current():
        # We need to avoid migration issues when changing ReportPeriod, where it is tryin to import it during migration
        try:
            return ReportPeriod.objects.order_by('-end')[0]
            # return ReportPeriod.objects.last()
        except Exception as e:
            pass

    @property
    def name_slug(self):
        # Todo: Improve it
        return self.name.replace('/', '-').replace(' ', '')

    @property
    def csv_fields_list(self):
        return self.csv_fields.split(',')


class ReportUpload(BaseUUIDModel, TimeStampedModel):
    user = models.ForeignKey(Account, help_text='Owner account')
    period = models.ForeignKey(ReportPeriod, null=True, blank=True, help_text='Period')

    file = CSVFileField(help_text='File storage')

    name = models.CharField(max_length=64, help_text='Name')
    description = models.TextField(blank=True, help_text='Description')

    class Meta:
        verbose_name = 'Report Upload'
        verbose_name_plural = 'Report Uploads'

    @property
    def s3_key(self):
        return f'{settings.AWS_LOCATION}/{self.file.name}'

    @property
    def s3_release_key(self):
        return f'{settings.AWS_RELEASE_LOCATION}/{self.period.name_slug}.csv'

    def release_copy_to_s3(self):
        s3 = boto3.client('s3')

        bucket = settings.APPDATA_BUCKET

        source_data = {
            'Bucket': bucket,
            'Key': self.s3_key
        }

        destination = self.s3_release_key

        s3.copy_object(Bucket=bucket, CopySource=source_data, Key=destination)

    def do_release(self, user):
        # Check for right date ordering
        release = getattr(self.period, 'release', None)

        if release:
            if release.report.created > self.created:
                raise AttributeError("Can't release upload")

        # Do the release
        if not release:
            release = ReportRelease.objects.create(period=self.period, report=self)

        # Update release information
        release.user = user
        release.report = self

        release.save()

        do_upload_release.delay(self.pk)

    def do_release_tasks(self):
        # Release tasks (delegated to celery):
        #   a. copy upload CSV to release CSV directly on S3
        #   b. clear all cache keys related with release period
        #   c. update manifest.json to reflect latest release changes
        #   d. generate release dataframe and cache it
        #   e. save filters payload
        #   f. cache updated manifest.json (see b)
        #   g. update agencies
        release = getattr(self.period, 'release', None)
        period = self.period

        if not release:
            raise AttributeError('Release does not exist')

        # a. copy relese to s3
        self.release_copy_to_s3()

        # b. clear all cache keys related with release period
        # We are not hashing periods in redis keys to easily locate it when cleaning on new release
        release_cache.delete_pattern(f'*{self.period.name}*')
        chart_cache.delete_pattern(f'*{self.period.name}*')

        # c. update static manifest file
        manifest = release.update_manifest()

        # d. generate release datafame and cache it
        metadata = ReleaseDataframe(period=self.period.name).cache_release_dataframe(
            return_metadata=True
        )

        # e. update agencies
        agencies = metadata.pop('agencies_data')

        Agency.update_from_data(agencies=agencies)

        # e. save filters payload - service level 1 options etc.
        period.metadata = metadata

        period.save()

        # f.cache updated manifest
        ReleaseManifest().set_to_cache(data=manifest)


class ReportRelease(BaseUUIDModel, TimeStampedModel, ReleaseManifestMixin):
    user = models.ForeignKey(Account, null=True, help_text='Owner account')
    report = models.OneToOneField(ReportUpload, null=True, help_text='Report upload')
    period = models.OneToOneField(ReportPeriod, help_text='Report period', related_name='release')

    class Meta:
        verbose_name = 'Report Release'
        verbose_name_plural = 'Report Releases'
        ordering = ['-created', ]


@receiver(pre_delete, sender=ReportRelease)
def flush_release_cache(sender, instance, **kwargs):
    # Flush cache on release delete
    release_cache.delete_pattern(f'*{instance.period.name}*')
    chart_cache.delete_pattern(f'*{instance.period.name}*')
