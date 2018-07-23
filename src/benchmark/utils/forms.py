from django import forms
from django.conf import settings

from crispy_forms.layout import Field
from crispy_forms.utils import (
    TEMPLATE_PACK, flatatt, get_template_pack, render_field,
)

class CustomField(Field):
    template = "template_tags/custom_field.html"

    def __init__(self, *args, **kwargs):
        self.grid_label_class = kwargs.pop('grid_label_class', None)
        self.grid_field_class = kwargs.pop('grid_field_class', None)
        super().__init__(*args, **kwargs)

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK):
        if hasattr(self, 'wrapper_class'):
            context['wrapper_class'] = self.wrapper_class

        if hasattr(self, 'grid_label_class'):
            context['grid_label_class'] = self.grid_label_class

        if hasattr(self, 'grid_field_class'):
            context['grid_field_class'] = self.grid_field_class

        html = ''

        for field in self.fields:
            html += render_field(
                field,
                form,
                form_style,
                context,
                template=self.template,
                attrs=self.attrs,
                template_pack=template_pack
            )

        return html


class PeriodBaseField(object):
    def __init__(self, *args, **kwargs):
        from benchmark.report.models import ReportPeriod

        if not kwargs.get('queryset'):
            kwargs['queryset'] = ReportPeriod.objects.all()
            kwargs['initial'] = [ReportPeriod.current()]


        return super().__init__(*args, **kwargs)


class PeriodModelChoiceField(PeriodBaseField, forms.ModelChoiceField):
    pass


class PeriodModelMultipleChoiceField(PeriodBaseField, forms.ModelMultipleChoiceField):
    pass
