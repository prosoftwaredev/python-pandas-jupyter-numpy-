import importlib

from chart import RELEASE_CACHE as cache

from notebooks.data_processing import clean_raw_dataframe


class ReleaseCache(object):
    dataframe = None
    period = ''
    cache = cache

    charts = {
        'wog_level1': 'notebooks.data_processing.build_wog_overview1_df',
        'wog_level2': 'notebooks.data_processing.build_wog_overview2_df',
        'myagency_level1': 'notebooks.data_processing.build_wog_overview2_df',
        'myagency_level2': 'notebooks.data_processing.build_wog_overview2_df',
        'myagency_level2_cost': 'notebooks.data_processing.build_wog_overview2_df'
    }

    def __init__(self, dataframe, period):
        self.dataframe = clean_raw_dataframe(dataframe)
        self.period = period

    def get_func(self, chart_key):
        module_parts = self.charts.get(chart_key).split('.')
        module_name, func_name = '.'.join(module_parts[:-1]), module_parts[-1]

        cls = importlib.import_module(module_name)

        return getattr(cls, func_name)

    def process(self):
        # Cache main dataframe to use in data export
        cache.set(f'{self.period}', self.dataframe.to_msgpack(compress='zlib'))

        print('starting caching')
        for chart_key, chart_module in self.charts.items():
            func = self.get_func(chart_key)
            df = func(raw_df=self.dataframe, use_cache=False)
            print(f'caching {chart_key}-{chart_module}')

            cache.set(f'{self.period}-{chart_key}', df.to_msgpack(compress='zlib'))
            print('cache successful')
