import io
import six
import base64
import boto3
import redis
import hashlib
import pickle
import importlib

from chardet.universaldetector import UniversalDetector

from django.conf import settings
from django.core.cache import caches
from django.utils.functional import SimpleLazyObject
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.sites.models import Site

import pandas as pd

from benchmark.chart.forms import FILTER_FIELDS_MAP
from benchmark.chart.exceptions import FilterParamsNotSupported
from benchmark.utils.json import json_loads


json_encoder = DjangoJSONEncoder()

RELEASE_CACHE = caches['releases']
CHART_CACHE = caches['charts']

GRAPH_IMPLEMENTED = [
    'wog_level1',
    'wog_level2',
    'wog_level2benchmark',
    'wog_level2trend',
    'myagency_level1',
    'myagency_level2',
    'myagency_level2_cost'
]


class S3Read(object):
    key = ''
    aws_key = ''

    def __init__(self, key=None, aws_key=None):
        if key:
            self.key = key
        if aws_key:
            self.aws_key = aws_key

    def get_from_s3(self, key=None):
        if not key:
            key = getattr(self, 'aws_key', None)

        if not key:
            raise AttributeError('Could not find AWS key.')

        s3 = boto3.client('s3')

        streaming_obj = s3.get_object(Bucket=settings.APPDATA_BUCKET, Key=key)

        obj = streaming_obj.get('Body', None)

        if obj:
            return obj.read()

    def read(self):
        return self.get_from_s3()


class S3OrRedis(S3Read):
    cache = RELEASE_CACHE
    key = '' # Cache key
    aws_key = '' # AWS object key

    def read(self, ignore_cache=None):
        if ignore_cache:
            data = self.get_from_s3()
            self.set_to_cache(data)

            return data

        data = self.cache.get(self.key)

        if not data:
            # Not in cache - read from S3 and save in cache
            data = self.get_from_s3()
            if data:
                self.set_to_cache(data)

        return data

    def json(self, ignore_cache=None):
        data = self.read(ignore_cache=ignore_cache)

        if isinstance(data, six.binary_type):
            data = data.decode('utf-8')
            data = json_loads(data)

        return data

    def set_to_cache(self, data):
        self.cache.set(self.key, data)


class ReleaseManifest(S3OrRedis):
    key = 'manifest'
    aws_key = settings.AWS_RELEASE_MANIFEST


class ReleaseDataframe(object):
    period = None

    def __init__(self, period):
        self.period = period

    def read_release_csv(self):
        manifest_stream = ReleaseManifest()

        manifest = manifest_stream.json(ignore_cache=True)

        if self.period not in manifest:
            raise AttributeError(f'Could not find selected period "{self.period}" in manifest.')

        release_csv = S3Read(key=self.period, aws_key=manifest[self.period]['upload'])
        print('found release_csv')
        return release_csv.read()

    def cache_release_dataframe(self, return_metadata=None):
        from chart.release import ReleaseCache

        release_csv = self.read_release_csv()

        release_stream = io.BytesIO(release_csv)

        detector = UniversalDetector()

        for line in release_stream.readlines():
            detector.feed(line)
            if detector.done: break

        detector.close()

        release_stream.seek(0)

        dataframe = pd.read_csv(release_stream, encoding=detector.result['encoding'])
        print(f'got dataframe of size {len(dataframe)}, going to set release_cache')
        release_cache = ReleaseCache(period=self.period, dataframe=dataframe)

        release_cache.process()
        print('processed release_cache')

        #self.cache_dataframe(key=self.period, dataframe=dataframe)

        if return_metadata:
            return self.get_release_dataframe_metadata(dataframe=dataframe)

        return dataframe

    def get_release_dataframe_metadata(self, dataframe):
        # Get release dataframe metadata to store in release model

        agency = list(dataframe['Agency name'].dropna().unique())
        agency_size = list(dataframe['Agency size'].dropna().unique())
        service_l1 = list(dataframe['Service classification'].dropna().unique())
        service_l2 = list(dataframe['Service name'].dropna().unique())
        unit_type = list(dataframe['Primary unit of measure'].dropna().unique())

        if 'Department' not in dataframe.columns:
            # To be consistent
            dataframe['Department'] = ''

        agencies_df = dataframe.groupby(['Agency name', 'Department']).agg({'Total cost': 'count'})
        agencies_df.reset_index(inplace=True)
        del agencies_df['Total cost']
        agencies_data = agencies_df.to_dict(orient='records')

        return {
            'agency': agency,
            'agency_size': agency_size,
            'service_level1': service_l1,
            'service_level2': service_l2,
            'unit_type': unit_type,
            'agencies_data': agencies_data
        }

    @staticmethod
    def read_release_dataframe(periods, df_key):
        results = []

        for period in periods:
            cache_data = RELEASE_CACHE.get(f'{period}-{df_key}')

            if not cache_data:
                # TODO: Run celery task to populate the cache, catch exception to show warning to the user
                raise KeyError(f'Cache for "{period}" period release dataframe not found.')

            results.append(pd.read_msgpack(cache_data))

        return results

    def cache_dataframe(self, key, dataframe):
        # TODO: Seems not needed and was moved to ReleaseCache
        if dataframe.empty:
            raise Exception('Could not cache empty dataframe!')

        RELEASE_CACHE.set(key, dataframe.to_msgpack(compress='zlib'))

        return dataframe


class ChartBase(object):
    periods = []   # Period - key for release dataframe, for multiple periods - listed in string separated by "--"
    key = None      # Key - key for chart type generated dataframe
    cache = CHART_CACHE
    session_key = None
    is_interactive = False
    deidentified = True
    browser = None
    chart_type = None
    level = None

    def __init__(self, periods, browser, chart_type, level, session_key, deidentified=True, *args, **kwargs):
        self.periods = periods
        self.browser = browser
        self.deidentified = deidentified
        self.chart_type = chart_type
        self.level = level
        self.session_key = session_key

        super().__init__(*args, **kwargs)

    @property
    def _filter_params(self):
        # TODO: We should get rid from this conversion by changing notebooks lib input params format
        params = {
            'agency': self.filter_params.get('Agency name'),
            'agency_size': self.filter_params.get('Agency size'),
            'service_level1': self.filter_params.get('Level 1 Service')
        }

        if self.chart_type in ['wog', 'myagency'] and self.level in ['level2', 'level2-cost-category']:
            params.update({
                'service_level2': self.filter_params.get('Level 2 Service')
            })
        else:
            if self.filter_params.get('Level 2 Service'):
                params.update({
                    'service_level2': [self.filter_params.get('Level 2 Service', {}).get('Service name')],
                    'unit_type': None,
                })
                if self.filter_params.get('Level 2 Service', {}).get('Primary unit of measure'):
                    params['unit_type'] = [self.filter_params.get('Level 2 Service', {}).get('Primary unit of measure')]

        return params

    @property
    def filter_fields(self):
        return [
                x for x in FILTER_FIELDS_MAP.get(self.chart_type, {}).get(self.level)
                    if x not in ['agency', 'asl', 'period']
            ]

    @property
    def _periods_list(self):
        if not isinstance(self.periods, list):
            # Let's use tuple based data structure even if there is only one dataframe
            return [self.periods]
        return self.periods

    @property
    def _periods(self):
        return '--'.join(self.periods)

    @property
    def cache_key(self):
        # Generate an unique key that referencing to user's session, chart and period, that can be used to clear cache
        if not self.periods or not self.key:
            raise AttributeError('You have to set key and period.')

        filter_params_hash = self.get_kwargs_hash(self.filter_params)

        return f'{self._periods}-{self.key}-{self.session_key}-{filter_params_hash}'

    def cache_dataframe(self, key, dataframe):
        if not isinstance(dataframe, tuple):
            # Let's use tuple based data structure even if there is only one dataframe
            dataframe = (dataframe, )

        empty_allowed = True

        # Do not cache empty dataframes - it is possible a bug somewhere that needs to be investigated before moving
        if not empty_allowed:
            for d in dataframe:
                if d.empty:
                    raise Exception('Could not cache empty dataframe!')

        cache_data = tuple(d.to_msgpack(compress='zlib') for d in dataframe)

        self.cache.set(key, cache_data)

        return dataframe

    def read_dataframe(self, ignore_cache=None):
        # Read generated(!) dataframe from Redis, otherwise cache it

        if not ignore_cache:
            cache_data = self.cache.get(self.cache_key)
            if cache_data:
                return tuple(pd.read_msgpack(cache_item) for cache_item in cache_data)

        # Get release dataframe from cache to use as a base to generate specific dataframe after
        release_dataframes = ReleaseDataframe.read_release_dataframe(periods=self.periods, df_key=self.df_key)

        release_dataframe = pd.concat(release_dataframes)

        dataframe = self.generate_dataframe(release_dataframe)

        return self.cache_dataframe(key=self.cache_key, dataframe=dataframe)


    def read_cache_dataframe(self):
        cache_data = self.cache.get(self.cache_key)

        if not cache_data:
            raise KeyError(f'Cache for "{self.cache_key}" dataframe not found.')

        return pd.read_msgpack(cache_data)

    def get_kwargs_hash(self, kwargs):
        return hashlib.md5(pickle.dumps(kwargs)).hexdigest()

    def get_draw_cache_key(self):
        return f'{self.cache_key}-graph'

    def get_filter_data_cache_key(self):
        return f'{self.cache_key}-filter_data'

    def get_filter_data(self):
        filter_data_cache_key = self.get_filter_data_cache_key()

        cache_data = self.cache.get(filter_data_cache_key)

        if cache_data:
            return cache_data

        release_dataframe = ReleaseDataframe.read_release_dataframe(periods=self.periods, df_key=self.df_key)

        release_dataframe = pd.concat(release_dataframe)

        results = {}

        try:
            results['agency_size'] = self.get_size_options(release_dataframe)
            results['service_level1'] = self.get_level1_service_options(release_dataframe)

            unit_type = {}

            if 'unit_type' in self.filter_fields:
                try:
                    unit_type = self.get_unit_type_options(release_dataframe)
                    results['unit_type'] = unit_type
                except KeyError as e:
                    pass

            results['service_level2'] = {}

            service_level2 = self.get_level2_service_options(release_dataframe) or {}

            if unit_type:
                # We should exclude level 2 services without unit types
                for service_name, service_options in service_level2.items():
                    level2_options = [x for x in service_options if results['unit_type'].get(x)]
                    if level2_options:
                        results['service_level2'][service_name] = level2_options
            else:
                results['service_level2'] = service_level2

        except NotImplementedError:
            return results

        self.cache.set(filter_data_cache_key, results)

        return results

    def draw(self):
        # Check for cache
        draw_cache_key = self.get_draw_cache_key()

        cache_data = self.cache.get(draw_cache_key)

        if cache_data:
            return cache_data

        filter_data = self.get_filter_data()

        # Some data stored in dict with key as depend field, so we should map it between each other:
        #    service_level2 = {
        #        <service_level_1>: [service_level2_options]
        #    }
        filter_value_fields = {
            'service_level2': 'service_level1',
            'unit_type': 'service_level2'
        }

        for filter_field in self.filter_fields:
            value_field = filter_value_fields.get(filter_field)
            field_value = self._filter_params.get(filter_field)
            allowed_options = filter_data.get(filter_field)

            if value_field:
                _allowed_options = []

                for option in self._filter_params.get(value_field):
                    _allowed_options += allowed_options.get(option)

                allowed_options = _allowed_options

            if field_value and not set(field_value).issubset(allowed_options):
                raise FilterParamsNotSupported()

        params = {
            'base_url': Site.objects.get_current().domain,
            'deidentified': self.deidentified,
            'browser': self.browser
        }

        if self.is_interactive:
            params.update({
                'interactive': self.is_interactive
            })

        dataframes = self.read_dataframe(ignore_cache=False)

        # It is tricky because we should return single dataframe as is, and if more than 1 df - return as a tuple
        result_dataframes = dataframes[0] if len(dataframes) == 1 else dataframes

        draw_results = self.generate_graph(result_dataframes, **params)

        # Cache it for future use
        self.cache.set(draw_cache_key, draw_results)

        return draw_results

    def generate_dataframe_(self, df):
        raise NotImplementedError('Generate dataframe is not implemented')

    def generate_graph_(self, df):
        raise NotImplementedError('Draw method is not implemented.')


class LazyChart(SimpleLazyObject):
    modules = {
        'wog-level1': 'chart.wog.level1',
        'wog-level2': 'chart.wog.level2',
        'wog-level2-benchmark': 'chart.wog.level2benchmark',
        'wog-level2-trend': 'chart.wog.level2trend',

        'myagency-level1': 'chart.agency.level1',
        'myagency-level2': 'chart.agency.level2',
        'myagency-level2-cost-category': 'chart.agency.level2cost'
    }

    def __init__(self, chart_type, level, **kwargs):
        kwargs.update({
            'chart_type': chart_type,
            'level': level
        })

        module_level = f'{chart_type}-{level}'

        if module_level not in self.modules:
            raise AttributeError(f'Chart module for "{module_level}" not found.')

        cls = importlib.import_module(self.modules[module_level]).Chart

        super().__init__(lambda: cls(**kwargs))
