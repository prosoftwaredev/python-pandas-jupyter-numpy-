import csv

from django import forms

from csvvalidator import CSVValidator
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Row, HTML, Field

from benchmark.account.models import Agency
from benchmark.report.models import ReportUpload, ReportPeriod

from benchmark.utils.models import validate_upload_file_extension
from benchmark.utils.forms import PeriodModelChoiceField, CustomField


class ReportUploadForm(forms.ModelForm):
    period = PeriodModelChoiceField()

    class Meta:
        model = ReportUpload
        fields = (
            'name',
            'description',
            'period',
            'file'
        )

    def __not_init__(self, *args, **kwargs):
        self.csv_fields = kwargs.pop('csv_fields')

        return super().__init__(*args, **kwargs)

    def clean_file(self):
        data = self.cleaned_data['file']

        period = self.cleaned_data['period']

        csv_fields = period.csv_fields_list

        # Since csv validator doesn't validate the whole CSV file syntax,
        # let's use exactly what we need - just first header row
        header_row = [data.file.readline().decode()]

        validator = CSVValidator(csv_fields)
        validator.add_header_check('EX1', 'bad header')

        # TODO: Add trim for header columns
        csv_data = csv.reader(header_row, delimiter=',')
        csv_validation_errors = validator.validate(csv_data)

        if csv_validation_errors:
            raise forms.ValidationError('Invalid CSV format (wrong fields definition).')

        return data


class ReportPeriodSelectForm(forms.Form):
    period = forms.ModelChoiceField(
        queryset=ReportPeriod.objects.all()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_errors = True
        self.helper.label_class = 'col-md-1'
        self.helper.field_class = 'col-md-3'


class ExportDatasetForm(forms.Form):
    period = PeriodModelChoiceField()
    agency = forms.ModelMultipleChoiceField(
        queryset=Agency.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not user.account.is_finance_admin:
            self.fields['agency'].queryset = user.account.agency.all()

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_errors = True
        self.helper.disable_csrf = True

        self.helper.layout = Layout(
                Div(
                    Field('period', tabindex='1'),
                    CustomField('agency', tabindex='2', grid_field_class='pre-scrollable'),
                    css_class="col-md-12"
                ),

        )