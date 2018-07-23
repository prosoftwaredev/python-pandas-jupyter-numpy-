from django.contrib.auth.views import logout
from django.conf.urls import url

from benchmark.report import views


urlpatterns = [
    # Upload
    url(r'^upload/$', views.ReportUploadListView.as_view(), name='report-upload-list'),
    url(r'^upload/add/$', views.ReportUploadCreateView.as_view(), name='report-upload-add'),

    # Release
    url(r'^release/add/$', views.ReportReleaseCreateView.as_view(), name='report-release-add'),

    # Export dataset
    url(r'^export/$', views.ExportDataset.as_view(), name='report-export-dataset'),
]
