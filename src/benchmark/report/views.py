import io

import pandas as pd

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.views.generic import CreateView, ListView, FormView, TemplateView
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormMixin
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy

from chart import RELEASE_CACHE as release_cache

from benchmark.report.models import ReportUpload, ReportRelease, ReportPeriod
from benchmark.report.forms import ReportUploadForm, ReportPeriodSelectForm, ExportDatasetForm

from benchmark.utils.decorators import role_finance_admin_required
from benchmark.utils.shortcuts import get_object_or_none


@method_decorator(role_finance_admin_required, name='dispatch')
class ReportUploadCreateView(FormView):
    model = ReportUpload
    form_class = ReportUploadForm
    template_name = 'report/add_upload.html'

    def get_form_kwargs_(self):
        kwargs = super().get_form_kwargs()

        period = get_object_or_404(ReportPeriod, pk=self.request.session.get('current_period', None))

        kwargs.update({
            'csv_fields': period.csv_fields_list
        })

        return kwargs

    def form_valid(self, form):
        obj = form.instance

        obj.user = self.request.user.account

        obj.save()

        context = self.get_context_data()

        context.update({
            'created': True
        })

        return render(self.request, self.template_name, context)


@method_decorator(role_finance_admin_required, name='dispatch')
class ReportUploadListView(ListView, FormView):
    template_name = 'report/list_upload.html'
    form_class = ReportPeriodSelectForm
    success_url = reverse_lazy('report-upload-list')

    ordering = '-created'

    queryset = ReportUpload.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()

        current_period = self.request.session.get('current_period', None)

        if current_period:
            qs = qs.filter(period__id=current_period)

        return qs

    def get_context_data(self):
        context = super().get_context_data()

        period = get_object_or_none(ReportPeriod, pk=self.request.session.get('current_period', None))

        period_release = getattr(period, 'release', None)

        context.update({
            'latest_release': period_release.report.created if period_release else None
        })

        return context

    def get_initial(self):
        initial = super().get_initial()

        initial['period'] = self.request.session.get('current_period', None)

        return initial

    def form_valid(self, form):
        self.request.session['current_period'] = str(form.cleaned_data['period'].pk)

        return super().form_valid(form)


@method_decorator(role_finance_admin_required, name='dispatch')
class ReportReleaseCreateView(CreateView):
    model = ReportRelease
    fields = ['report', ]
    success_url = reverse_lazy('report-upload-list')

    def form_valid(self, form):
        report = form.cleaned_data['report']

        report.do_release(user=self.request.user.account)

        messages.success(self.request, 'Upload successfully released.')

        return redirect(self.success_url)


@method_decorator(login_required, name='dispatch')
class ExportDataset(FormView):
    """Export agency data in CSV format."""
    template_name = 'report/export_dataset.html'
    form_class = ExportDatasetForm

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super().get_form_kwargs(*args, **kwargs)

        form_kwargs['user'] = self.request.user

        return form_kwargs

    def form_valid(self, form):
        data = form.cleaned_data

        dataframe = release_cache.get(f"{data['period'].name}")

        if not dataframe:
            return render(self.request, self.template_name, {'form': form, 'no_data': True})

        dataframe = pd.read_msgpack(dataframe)

        agencies = data['agency'].values_list('code', flat=True)
        data_slice = dataframe.loc[dataframe['Agency name'].isin(agencies)]

        stream = data_slice.to_csv(index=False)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f"filename={data['period'].name}-agencies.csv"

        response.write(stream)

        return response
