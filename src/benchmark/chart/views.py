import six
import json
from urllib.parse import urlencode

from functools import reduce

from django.http import Http404
from django.urls import reverse
from django.views.generic import FormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from chart import LazyChart

from benchmark.utils.http import get_lazy_request_browser
from benchmark.account.models import Agency
from benchmark.chart import forms
from benchmark.chart.exceptions import FilterParamsNotSupported
from benchmark.report.models import ReportRelease, ReportPeriod


CHART_FORM_LIST = {
    'wog': {
        'level1': forms.WholeGovernmentLevel1Form,
        'level2': forms.WholeGovernmentLevel2Form,
        'level2-benchmark': forms.WholeGovernmentLevel2BenchmarkForm,
        'level2-trend': forms.WholeGovernmentLevel2TrendForm
    },
    'myagency': {
        'level1': forms.MyAgencyLevel1Form,
        'level2': forms.MyAgencyLevel2Form,
        'level2-cost-category': forms.MyAgencyLevel2CostCategoryForm
    }
}

FILTERS_SESSION_KEY = 'filter_params'


def flush_filter_preferences(request, chart_type, level):
    preferences = request.session.get(FILTERS_SESSION_KEY, {}).get(chart_type, {})

    preferences[level] = {}

    request.session.update({
        FILTERS_SESSION_KEY: {
            chart_type: preferences
        }
    })


def get_chart(request, chart_type, level, period=None, process_chart=True, **kwargs):
    if not period:
        period = [ReportPeriod.current().name, ]

    if isinstance(period, six.string_types):
        period = [period, ]

    fields = forms.FILTER_FIELDS_MAP.get(chart_type, {}).get(level)

    if not fields:
        raise AttributeError('Unknown chart and level type.')

    for field_name, field_type in fields.items():
        # Only these two params should be passed as single string value,
        # all othter params are lists
        if not (field_name in ['service_level2', 'unit_type'] and field_type == 'dropdown'
                and level != 'level2-cost-category'):
            if field_name != 'asl':
                field_value = kwargs.get(field_name)
                if isinstance(field_value, six.string_types):
                    # If not iterable - make it
                    kwargs[field_name] = [field_value, ]

    financial_year = list(ReportPeriod.objects.filter(name__in=period).values_list('financial_year', flat=True))

    filter_params = {
        'Agency name': kwargs.get('agency') or [],
        'Agency size': kwargs.get('agency_size', []) or [],
        'Financial Year': financial_year,
        'Level 1 Service': kwargs.get('service_level1', [])
    }

    if chart_type == 'wog' and level != 'level2-trend':
        filter_params.update({
            'ASL': kwargs.get('asl') if kwargs.get('asl') == 'True' else ''
        })

    if fields.get('service_level2'):
        filter_params.update({
            'Level 2 Service': {
                'Service name': kwargs.get('service_level2', ''),
                'Primary unit of measure': kwargs.get('unit_type', '')
            }
        })

    if chart_type == 'myagency' and level == 'level1':
        filter_params.update({
            'ASL': kwargs.get('asl') if kwargs.get('asl') == 'True' else ''
        })
        del filter_params['Agency size']
        del filter_params['Level 1 Service']

    if chart_type in ['wog', 'myagency'] and level in ['level2', 'level2-cost-category']:
        filter_params['Level 2 Service'] = kwargs.get('service_level2', [])

    browser = get_lazy_request_browser(user_agent=request.META['HTTP_USER_AGENT'])

    if process_chart:
        chart = LazyChart(
            chart_type=chart_type,
            level=level,
            periods=period,
            filter_params=filter_params,
            browser=browser,
            session_key=request.session.session_key,
            deidentified=kwargs.get('deidentified', True)
        )
    else:
        chart = None

    # Prepare debug info
    _filter_params = {'Period': period}
    _filter_params.update(filter_params)

    return chart, _filter_params


def get_chart_initial(request, user, level, chart_type):
    # Show only related user agencies
    if user.account.is_finance_admin:
        default_agencies = Agency.objects.order_by('code')
    else:
        default_agencies = user.account.agency.all().order_by('code')

    default_periods = ReportPeriod.objects.filter(release__isnull=False)

    default_filters = {
        'wog': {
            'level1': {
                'period': default_periods,
                'asl': '',
                'agency': ['First'],
                'agency_size': ['All'],
                'service_level1': ['Corporate Services Functions', 'Financial Services Functions',
                                   'Human Resource Services Functions'],
            },
            'level2': {
                'period': default_periods,
                'asl': '',
                'agency': ['First'],
                'agency_size': ['All'],
                'service_level1': 'Financial Services Functions',  # Drill down on Financial Services
                'service_level2': ['All'],
            },
            'level2-benchmark': {
                # Kludge because for some reason, other code expects QuerySets here instead of lists
                'period': ReportPeriod.objects.filter(id=ReportPeriod.current().id),
                'asl': '',
                'agency': ['First'],
                'agency_size': ['All'],
                'service_level1': ['Financial Services Functions'],
                'service_level2': 'Credit Card Management',
                'unit_type': 'Average # of cards managed',
            },
            'level2-trend': {
                'period': default_periods,
                'agency': ['First'],
                'agency_size': ['All'],
                'service_level1': ['Financial Services Functions'],
                'service_level2': 'Accounts Payable',
                'unit_type': '# of manual AP invoices',
            }

        },
        'myagency': {
            'level1': {
                'period': default_periods[:1],
                'asl': '',
                'agency': ['First'],
                'service_level1': None
            },
            'level2': {
                'period':  default_periods,
                'agency': ['First'],
                'agency_size': ['All'],
                'service_level1': ['Financial Services Functions'],
                'service_level2': ['All']
            },
            'level2-cost-category': {
                # bug when selecting more than one period
                'period': default_periods,
                'agency_size': ['All'],
                'agency': ['First'],
                'service_level1': ['Financial Services Functions'],
                'service_level2': ['Credit Card Management']
            }
        }
    }

    default = default_filters[chart_type][level]

    if default.get('agency') == ['First']:
        # Get intersection between all periods agencies - like in js filters
        _period_agencies = [set(p.metadata['agency']) for p in default['period']]

        if _period_agencies:
            period_agencies = list(reduce(set.intersection, _period_agencies))

        default['agency'] = default_agencies.filter(code__in=period_agencies).values_list('code', flat=True).first()

    default['period'] = list(default['period'].values_list('name', flat=True))

    # Use saved filter params from the session
    for field, value in request.session.get(FILTERS_SESSION_KEY, {}).get(chart_type, {}).get(level, {}).items():
        # TODO: Change it across the whole app to use it from periods intersected metadata
        if value == ['All'] and field == 'agency_size':
            value = [
                'Extra Large agencies', 'Large agencies', 'Medium agencies',
                'Small agencies', 'Extra Small agencies', 'Micro'
            ]
        default[field] = value

    if 'agency_all_across' in request.session:
        default['agency'] = [request.session['agency_all_across']]

    return default


@method_decorator(login_required, name='dispatch')
class ChartBaseView(FormView):
    """Base chart pages"""
    chart_type = ''
    template_name = 'chart/charts.html'

    def get_form_class(self):
        level = self.kwargs.get('level', None)
        if level not in CHART_FORM_LIST.get(self.chart_type, {}):
            raise Http404('Selected level is not supported.')

        return CHART_FORM_LIST[self.chart_type][level]

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super().get_form_kwargs(*args, **kwargs)

        form_kwargs.update({
            'user': self.request.user
        })

        if self.request.GET:
            form_kwargs.update({
                'data': self.request.GET
            })

        return form_kwargs

    def get_context_data(self,*args,**kwargs):
        context = super().get_context_data(*args,**kwargs)

        results = {}
        level = self.kwargs.get('level', None)

        if self.request.GET:
            form_cls = self.get_form_class()
            form = form_cls(data=self.request.GET, user=self.request.user)

            if form.is_valid():
                data = form.cleaned_data

                # Save agency as session if only one agency name selected
                if isinstance(data['agency'], str) and data['agency'] != 'All':
                    self.request.session['agency_all_across'] = data['agency']
                elif len(data['agency']) == 1 and data['agency'][0] != 'All':
                    self.request.session['agency_all_across'] = data['agency'][0]
                else:
                    if 'agency_all_across' in self.request.session:
                        del self.request.session['agency_all_across']

                flush_filter_preferences(self.request, self.chart_type, level)

                # Handle session filters - save filters from GET params into session
                fields = forms.FILTER_FIELDS_MAP.get(self.chart_type, {}).get(level)
                for field, field_value in data.items():
                    # Determine field type and convert to apropriate format (list or single value string)
                    if fields.get(field) == 'checkbox' and not isinstance(field_value, (list, tuple)):
                        field_value = [field_value]

                    self.request.session[FILTERS_SESSION_KEY][self.chart_type][level][field] = field_value
            else:
                data = form.cleaned_data
                # TODO: Add better errors formating here
                results = {
                    'errors': [
                        "The data doesn't currently support the filters you've supplied for this period:"
                    ] + [', '.join(e) for k, e in form.errors.items()]
                }
        else:
            data = get_chart_initial(
                request=self.request,
                user=self.request.user,
                chart_type=self.chart_type,
                level=level
            )

        initial_data = dict(data)

        if 'service_level2' not in initial_data and self.chart_type == 'wog' and level == 'level2':
            initial_data['service_level2'] = ['All']

        # Let's do the trick to meet charts requirements
        for key, value in data.items():
            if value == ['All'] and key == 'agency_size':
                data[key] = [
                    'Extra Large agencies', 'Large agencies', 'Medium agencies',
                    'Small agencies', 'Extra Small agencies', 'Micro'
                ]
            elif value == 'All':
                data[key] = ''
            elif value == ['All']:
                data[key] = []

        chart, filter_params = get_chart(
            request=self.request,
            chart_type=self.chart_type,
            level=level,
            deidentified=False if self.request.user.account.is_finance_admin else True,
            process_chart='errors' not in results,
            **data
        )

        l2_service_name = ''
        if 'Level 2 Service' in filter_params:
            if isinstance(filter_params['Level 2 Service'], list):
                if len(filter_params['Level 2 Service']) > 0:
                    l2_service_name = filter_params['Level 2 Service'][0]
            else:
                l2_service_name = filter_params['Level 2 Service']['Service name']

        # Get level 2 services and unit type based on service 1 (which is based on other filter options)
        periods = {}
        user_agencies = [x.code for x in self.request.user.account.agency.all()]
        for period in ReportPeriod.objects.filter(release__isnull=False).exclude(name='Test'):
            period_chart, fp = get_chart(
                request=self.request,
                chart_type=self.chart_type,
                level=level,
                period=[period.name]
            )

            filter_data = period_chart.get_filter_data()

            periods[period.name] = {}

            # Deidentified check
            # Finance admin can access all identified agencies
            if self.request.user.account.is_finance_admin:
                periods[period.name].update({
                    'agency': sorted(period.metadata['agency'])
                })
            else:
                # Finance user can access only his identified agencies
                periods[period.name].update({
                    'agency': sorted(list(set(user_agencies).intersection(period.metadata['agency'])))
                })

            periods[period.name].update(filter_data)

        default_list_values = list(periods.values())[0]

        if not results.get('errors'):
            # Let's catch all exceptions here, to avoid not nice application crash
            try:
                results = chart.draw()
            except FilterParamsNotSupported:
                # Flush bad params from the saved preferences
                flush_filter_preferences(self.request, self.chart_type, level)

                results = {
                    'errors': ["The data doesn't currently support the filters you've supplied for this period."]
                }

            if self.chart_type == 'wog' and level == 'level2':
                wog_level2_drill_down_remove_params = ['service_level2', 'period']
                drill_down_url_dict = {
                    key: value for key, value in initial_data.items() if key not in wog_level2_drill_down_remove_params
                }
                if 'agency' not in drill_down_url_dict or len(drill_down_url_dict['agency']) == 0:
                    try:
                        drill_down_url_dict['agency'] = default_list_values['agency'][0]
                    except:
                        drill_down_url_dict['agency'] = 'Agency 1'
                drill_down_url = urlencode(drill_down_url_dict, True)
            else:
                drill_down_url = None

            context['drill_down_url'] = drill_down_url

        if results.get('errors'):
            # If any errors occured (i,e, filters did not yeild any data point) - remove saved filters
            flush_filter_preferences(self.request, self.chart_type, level)

        context.update({
            'results': results,
            'chart_type': self.chart_type,
            'level': level,
            'filter_params': filter_params,
            'initial_data': initial_data,
            'user_agent': self.request.META['HTTP_USER_AGENT'],
            'default_list_values': default_list_values,
            'l2_service_name': l2_service_name,
            'period_mapping': json.dumps({x.financial_year: x.name for x in ReportPeriod.objects.all()})
        })

        return context


@method_decorator(login_required, name='dispatch')
class FiltersPage(FormView):
    """Separate filters page, suitable for every chart we have."""
    template_name = 'chart/filters.html'

    def get_form_class(self):
        level = self.kwargs.get('level', None)
        chart_type = self.kwargs.get('chart_type')

        if level not in CHART_FORM_LIST.get(chart_type, {}):
            raise Http404('Selected level is not supported.')

        return CHART_FORM_LIST[chart_type][level]

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super().get_form_kwargs(*args, **kwargs)

        form_kwargs['user'] = self.request.user

        if self.request.GET:
            form_kwargs.update({
                'data': self.request.GET
            })

        return form_kwargs

    def get_context_data(self,*args,**kwargs):
        context = super().get_context_data(*args,**kwargs)

        data = None
        level = self.kwargs.get('level', None)
        chart_type = self.kwargs.get('chart_type', None)

        context.update({
            'chart_absolute_url': reverse(
                f'chart-whole-government-{level}' if chart_type == 'wog' else f'chart-my-agency-{level}'
            )
        })

        if self.request.GET:
            form_cls = self.get_form_class()
            form = form_cls(data=self.request.GET, user=self.request.user)

            if form.is_valid():
                data = form.cleaned_data

        if not data:
            data = get_chart_initial(request=self.request,
                                    user=self.request.user,
                                    chart_type=self.kwargs.get('chart_type'),
                                    level=self.kwargs.get('level'))

        initial_data = dict(data)

        if 'service_level2' not in initial_data and self.kwargs.get('chart_type') == 'wog' and self.kwargs.get('level') == 'level2':
            initial_data['service_level2'] = ['All']

        fields = forms.FILTER_FIELDS_MAP.get(chart_type, {}).get(level)

        # Get level 2 services and unit type based on service 1 (which is based on other filter options)
        periods = {}
        user_agencies = [x.code for x in self.request.user.account.agency.all()]
        for period in ReportPeriod.objects.filter(release__isnull=False).exclude(name='Test'):
            period_chart, fp = get_chart(
                request=self.request,
                chart_type=chart_type,
                level=level,
                period=[period.name])

            filter_data = period_chart.get_filter_data()

            periods[period.name] = {}

            # Deidentified check
            # Finance admin can access all identified agencies
            if self.request.user.account.is_finance_admin:
                periods[period.name].update({
                    'agency': sorted(period.metadata['agency'])
                })
            else:
                # Finance user can access only his identified agencies
                periods[period.name].update({
                    'agency': sorted(list(set(user_agencies).intersection(period.metadata['agency'])))
                })

            # remove major projects, other non corporate and pass through
            # as selection options under the level 1 services in WofG views
            if chart_type == 'wog' or chart_type == 'myagency':
                if 'service_level1' in filter_data:
                    filter_data['service_level1'] = [
                        option for option in filter_data['service_level1']
                        if option.lower() not in ['major projects', 'other non corporate', 'pass through']
                    ]

            periods[period.name].update(filter_data)

        context.update({
            'period_data': periods
        })

        default_list_values = list(periods.values())[0]

        context.update({
            'filter_fields_map': forms.FILTER_FIELDS_MAP,
            'chart_type': chart_type,
            'initial_data': initial_data,
            'level': level,
            'default_list_values': default_list_values
        })

        return context

class WholeGovernmentLevel1(ChartBaseView):
    chart_type = 'wog'
    template_name = 'chart/wofg-level1.html'


class WholeGovernmentLevel2(ChartBaseView):
    chart_type = 'wog'
    template_name = 'chart/wofg-level2.html'


class WholeGovernmentLevel2Benchmark(ChartBaseView):
    chart_type = 'wog'
    template_name = 'chart/wofg-level2-benchmark.html'


class MyAgencyLevel1(ChartBaseView):
    chart_type = 'myagency'
    template_name = 'chart/myagency-level1.html'


class MyAgencyCostCategoryBreakdown(ChartBaseView):
    chart_type = 'myagency'
    template_name = 'chart/myagency-level2-cost-category-breakdown.html'


class WholeGovernment(ChartBaseView):
    """Whole of Government charts set."""
    chart_type = 'wog'


class MyAgency(ChartBaseView):
    """My agency charts set."""
    chart_type = 'myagency'