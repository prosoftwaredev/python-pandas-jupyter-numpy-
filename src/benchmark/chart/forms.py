from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Row, HTML, Field


FILTER_FIELDS_MAP = {
    'wog': {
        'level1': {
            'period': 'checkbox',
            'asl': 'checkbox',
            'agency': 'checkbox',
            'agency_size': 'checkbox',
            'service_level1': 'checkbox',
        },
        'level2': {
            'period': 'checkbox',
            'asl': 'checkbox',
            'agency': 'checkbox',
            'agency_size': 'checkbox',
            'service_level1': 'dropdown',
            'service_level2': 'checkbox'
        },
        'level2-benchmark': {
            'period': 'dropdown',
            'asl': 'checkbox',
            'agency': 'dropdown',
            'agency_size': 'checkbox',
            'service_level1': 'dropdown',
            'service_level2': 'dropdown',
            'unit_type': 'dropdown'
        },
        'level2-trend': {
            'period': 'checkbox',
            'agency': 'dropdown',
            'agency_size': 'checkbox',
            'service_level1': 'dropdown',
            'service_level2': 'dropdown',
            'unit_type': 'dropdown'
        }
    },
    'myagency': {
        'level1': {
            'period': 'dropdown',
            'asl': 'checkbox',
            'agency': 'dropdown',
            'service_level1': 'checkbox',
        },
        'level2': {
            'period': 'checkbox',
            'agency': 'dropdown',
            'agency_size': 'checkbox',
            'service_level1': 'dropdown',
            'service_level2': 'checkbox'
        },
        'level2-cost-category': {
            'period': 'checkbox',
            'agency': 'checkbox',
            'agency_size': 'checkbox',
            'service_level1': 'dropdown',
            'service_level2': 'dropdown'
        },
    }
}


class MultipleChoiceFieldNoValidate(forms.MultipleChoiceField):
    def validate(self, *args, **kwargs):
        pass


class ChoiceFieldNoValidate(forms.ChoiceField):
    def validate(self, *args, **kwargs):
        pass


class BaseValidationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)

        return super().__init__(*args, **kwargs)

    def clean_period(self):
        from benchmark.report.models import ReportRelease
        value = self.cleaned_data.get('period')

        _value = [value] if not isinstance(value, list) else value

        # Check if period exists
        allowed_values = ReportRelease.objects.all().values_list('report__period__name', flat=True)
        not_matching_values = [x for x in _value if x not in allowed_values]

        if  not_matching_values:
            wrong_data = ', '.join(not_matching_values)
            word = 'Periods' if len(not_matching_values) > 1 else 'Period'
            raise forms.ValidationError(f'{word} "{wrong_data}" does not exist.')

        return value

    def clean_agency(self):
        value = self.cleaned_data.get('agency')

        _value = [value] if not isinstance(value, list) else value

        if not self.user.account.is_finance_admin:
            # If agency user - allow only authorised agencies
            allowed_values = list(self.user.account.agency.all().values_list('code', flat=True))
            not_matching_values = [x for x in _value if x not in allowed_values]

            if not_matching_values:
                wrong_data = ', '.join(not_matching_values)
                word = 'Agencies' if len(not_matching_values) > 1 else 'Agency'
                raise forms.ValidationError(f'{word} "{wrong_data}" is not allowed.')

        return value


class WholeGovernmentBaseForm(BaseValidationForm):
    period = MultipleChoiceFieldNoValidate(required=False, label='Period', widget=forms.CheckboxSelectMultiple())
    asl = ChoiceFieldNoValidate(required=False, label='ASL', widget=forms.CheckboxInput())
    agency = MultipleChoiceFieldNoValidate(required=False, label='Agency name', widget=forms.CheckboxSelectMultiple())
    agency_size = MultipleChoiceFieldNoValidate(required=False, label='Agency size',
                                                widget=forms.CheckboxSelectMultiple())
    service_level1 = MultipleChoiceFieldNoValidate(required=False, label='Level 1 services',
                                                   widget=forms.CheckboxSelectMultiple())

    form_title = 'WofG Level 1 Services'

    form_chart_type = 'wog_level1'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_errors = True
        self.helper.disable_csrf = True

        self.helper.layout = Layout(
            HTML("""<legend>Select chart filters</legend>"""),
            Div(
                Div(
                    Field('period', tabindex='1'),
                    Field('asl', tabindex='2'),
                    Field('agency', tabindex='3'),
                    Field('agency_size', tabindex='5'),
                    css_class="col-md-6"
                ),
                Div(
                    Field('service_level1', tabindex='6'),
                    css_class="col-md-6"
                ),
                css_class='row'
            )
        )


class WholeGovernmentLevel1Form(WholeGovernmentBaseForm):
    pass


class WholeGovernmentLevel2Form(WholeGovernmentBaseForm):
    service_level1 = ChoiceFieldNoValidate(required=False, label='Level 1 services', widget=forms.RadioSelect())
    service_level2 = MultipleChoiceFieldNoValidate(required=False, label='Level 2 service',
                                                   widget=forms.CheckboxSelectMultiple())

    form_title = 'Level 2 Services'

    form_chart_type = 'wog_level2'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_errors = True
        self.helper.disable_csrf = True

        self.helper.layout = Layout(
            HTML("""<legend>Select chart filters</legend>"""),
            Div(
                Div(
                    Field('period', tabindex='1'),
                    Field('asl', tabindex='2'),
                    Field('agency', tabindex='3'),
                    Field('agency_size', tabindex='4'),
                    css_class="col-md-6"
                ),
                Div(
                    Field('service_level1', tabindex='5'),
                    Field('service_level2', tabindex='6'),
                    css_class="col-md-6"
                ),
                css_class='row'
            )
        )


class WholeGovernmentLevel2BenchmarkForm(WholeGovernmentBaseForm):
    period = ChoiceFieldNoValidate(required=False, label='Period')
    service_level1 = ChoiceFieldNoValidate(required=False, label='Level 1 services')
    service_level2 = ChoiceFieldNoValidate(required=False, label='Level 2 service')
    unit_type = ChoiceFieldNoValidate(required=False, label='Primary unit of measure')

    form_title = 'Level 2 Benchmark'

    form_chart_type = 'wog_benchmark_level2'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_errors = True
        self.helper.disable_csrf = True

        self.helper.layout = Layout(
            HTML("""<legend>Select chart filters</legend>"""),
            Div(
                Div(
                    Field('period', tabindex='1'),
                    Field('asl', tabindex='2'),
                    Field('agency', tabindex='3'),
                    Field('agency_size', tabindex='4'),
                    css_class="col-md-6"
                ),
                Div(
                    Field('service_level1', tabindex='5'),
                    Field('service_level2', tabindex='6'),
                    Field('unit_type', tabindex='7'),
                    css_class="col-md-6"
                ),
                css_class='row'
            )
        )


class WholeGovernmentLevel2TrendForm(WholeGovernmentBaseForm):
    agency = ChoiceFieldNoValidate(required=False, label='Agency name')
    service_level1 = ChoiceFieldNoValidate(required=False, label='Level 1 services')
    service_level2 = ChoiceFieldNoValidate(required=False, label='Level 2 service')
    unit_type = ChoiceFieldNoValidate(required=False, label='Primary unit of measure')

    form_title = 'Level 2 Trend'

    form_chart_type = 'wog_trend_level2'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_errors = True
        self.helper.disable_csrf = True

        self.helper.layout = Layout(
            HTML("""<legend>Select chart filters</legend>"""),
            Div(
                Div(
                    Field('period', tabindex='1'),
                    Field('agency', tabindex='2'),
                    Field('agency_size', tabindex='3'),
                    css_class="col-md-6"
                ),
                Div(
                    Field('service_level1', tabindex='4'),
                    Field('service_level2', tabindex='5'),
                    Field('unit_type', tabindex='6'),
                    css_class="col-md-6"
                ),
                css_class='row'
            )
        )


class MyAgencyBaseForm(BaseValidationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_errors = True
        self.helper.disable_csrf = True


class MyAgencyLevel1Form(MyAgencyBaseForm):
    period = ChoiceFieldNoValidate(required=False, label='Period', widget=forms.RadioSelect())
    asl = ChoiceFieldNoValidate(required=False, label='ASL', widget=forms.CheckboxInput())
    agency = MultipleChoiceFieldNoValidate(required=False, label='Agency name')
    service_level1 = MultipleChoiceFieldNoValidate(required=False, label='Level 1 services',
                                                   widget=forms.CheckboxSelectMultiple())

    form_title = 'Level 1 Dashboard'


class MyAgencyLevel2Form(MyAgencyBaseForm):
    period = MultipleChoiceFieldNoValidate(required=False, label='Period', widget=forms.CheckboxSelectMultiple())
    agency = ChoiceFieldNoValidate(required=False, label='Agency name')
    agency_size = MultipleChoiceFieldNoValidate(
        required=False,
        label='Agency size',
        widget=forms.CheckboxSelectMultiple()
    )

    service_level1 = ChoiceFieldNoValidate(required=False, label='Level 1 services')
    service_level2 = MultipleChoiceFieldNoValidate(
        required=False,
        label='Level 2 service',
        widget=forms.CheckboxSelectMultiple()
    )

    form_title = 'Level 2 Dashboard'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_errors = True
        self.helper.disable_csrf = True

        self.helper.layout = Layout(
            HTML("""<legend>Select chart filters</legend>"""),
            Div(
                Div(
                    Field('period', tabindex='1'),
                    Field('agency', tabindex='2'),
                    Field('agency_size', tabindex='3'),
                    css_class="col-md-6"
                ),
                Div(
                    Field('service_level1', tabindex='4'),
                    Field('service_level2', tabindex='5'),

                    css_class="col-md-6"
                ),
                css_class='row'
            )
        )


class MyAgencyLevel2CostCategoryForm(MyAgencyBaseForm):
    period = MultipleChoiceFieldNoValidate(required=False, label='Period', widget=forms.CheckboxSelectMultiple())
    agency = MultipleChoiceFieldNoValidate(required=False, label='Agency name')

    agency_size = MultipleChoiceFieldNoValidate(
        required=False,
        label='Agency size',
        widget=forms.CheckboxSelectMultiple()
    )

    service_level1 = ChoiceFieldNoValidate(required=False, label='Level 1 services')
    service_level2 = ChoiceFieldNoValidate(required=False, label='Level 2 service')

    form_title = 'Cost Category Breakdown'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_errors = True
        self.helper.disable_csrf = True

        self.helper.layout = Layout(
            HTML("""<legend>Select chart filters</legend>"""),
            Div(
                Div(
                    Field('period', tabindex='1'),
                    Field('agency', tabindex='2'),
                    Field('agency_size', tabindex='3'),
                    css_class="col-md-6"
                ),
                Div(
                    Field('service_level1', tabindex='4'),
                    Field('service_level2', tabindex='5'),

                    css_class="col-md-6"
                ),
                css_class='row'
            )
        )
