import boto3
import json

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.core.cache import caches


json_encoder = DjangoJSONEncoder()


class ReleaseManifestMixin(object):
    cache = caches['releases']

    def load_manifest(self):
        # Todo: Add caching here
        s3 = boto3.client('s3')

        bucket = settings.APPDATA_BUCKET

        try:
            streaming_obj = s3.get_object(Bucket=bucket, Key=settings.AWS_RELEASE_MANIFEST)

            obj = streaming_obj.get('Body', None)

            if obj:
                manifest_data = obj.read()
        except Exception as e:
            # Load default manifest
            manifest_data = '{}'

        return json.loads(manifest_data)

    def save_to_manifest(self, release_manifest):
        s3 = boto3.resource('s3')

        bucket = s3.Bucket(settings.APPDATA_BUCKET)

        manifest_data = json_encoder.encode(release_manifest)

        result = bucket.put_object(Key=settings.AWS_RELEASE_MANIFEST, Body=manifest_data)

        return result

    def generate_release_manifest(self):
        # Generate manifest entry for current release
        manifest = self.load_manifest()

        release_manifest = {
            self.period.name: {     # name_slug
                'upload': self.report.s3_release_key,
                'updated': self.modified
            }
        }

        manifest.update(release_manifest)

        return manifest

    def update_manifest(self):
        release_manifest = self.generate_release_manifest()

        print(release_manifest)

        res = self.save_to_manifest(release_manifest=release_manifest)

        print(res)

        return release_manifest