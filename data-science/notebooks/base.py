from operator import itemgetter
from io import BytesIO
import base64
import furl


class ChartBase(object):

    def __init__(self, filter_params):
        self.filter_params = filter_params

    def convert_figure_to_base64(self, fig):
        if isinstance(fig, str):
            return fig
        else:
            fig_bytesio = BytesIO()
            fig.savefig(fig_bytesio, format='png', bbox_inches='tight')
            fig_bytesio.seek(0)
            b64_string = 'data:image/png;base64,' + base64.b64encode(fig_bytesio.read()).decode("utf-8")
            return '<img class="dataframe chart" src="%s">' % b64_string

    def format_amount(self, x ,i):
        if x < 1000:
            return '${:,.0f}'.format(x)
        else:
            return '${:,.0f}k'.format(x/1000)

    def get_size_options(self, df):
        df = self.filter_dataframe(df)
        sizes = df['Agency size'].dropna().unique()
        expected_sizes = ['Extra Large agencies', 'Large agencies', 'Medium agencies', 'Small agencies', 'Extra Small agencies', 'Micro']
        sizes = [(x, expected_sizes.index(x)) for x in sizes]
        sizes.sort(key=itemgetter(1), reverse=True)
        return [x[0] for x in sizes]

    def get_level1_service_options(self, df):
        df = self.filter_dataframe(df)
        service_names = df['Service classification'].dropna().unique()
        return sorted(list(service_names))

    def get_level2_service_options(self, df):
        df = self.filter_dataframe(df)
        xdf = df.groupby(['Service classification', 'Service name']).agg({'Agency name': 'count'})
        options_map = {x: list(xdf.loc[x].index) for x,y in xdf.index}
        return options_map

    def get_unit_type_options(self, df):
        df = self.filter_dataframe(df)
        xdf = df.groupby(['Service name', 'Primary unit of measure']).agg({'Agency name': 'count'})
        options_map = {x: list(xdf.loc[x].index) for x,y in xdf.index}
        return options_map

    def create_url_mapping(self, labels, filter_params, drilldown_on, base_url, l2tol1_map=None):
        # Translate filters
        key_map = {
            'Agency name': 'agency',
            'Agency size': 'size',
            'Financial Year': 'period',
            'Level 1 Service': 'service_level1',
            'Level 2 Service': 'service_level2'
        }
        filters = {key_map.get(k, k): v for k,v in filter_params.items() if type(v) == list}
        if 'period' in filters.keys():
            def format_year(year): return '/'.join([x[::-1][0:2][::-1] for x in year.split('-')]) + 'FY'
            filters['period'] = [format_year(x) for x in filters['period']]
        # Build label-to-URL mapping
        urls = {}
        for label in labels:
            f = furl.furl('')
            filters[drilldown_on] = label
            if l2tol1_map:
                filters['service_level1'] = l2tol1_map[label]
            f.args = filters
            url = base_url + f.url + '&search='
            urls[label] = url
        return urls

    def filter_dataframe(self, df):
        raise NotImplementedError('Filter dataframe is not implemented')

    def generate_dataframe(self, release_dataframe):
        raise NotImplementedError('Generate dataframe is not implemented')

    def generate_graph(self, filter_params):
        raise NotImplementedError('Generate graph method is not implemented.')
