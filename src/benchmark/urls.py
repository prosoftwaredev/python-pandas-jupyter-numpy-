from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

def test500(request):
    raise NotImplementedError('Test')


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^healthcheck', lambda r: HttpResponse()),

    url(r'^account/', include('benchmark.account.urls')),
    url(r'^report/', include('benchmark.report.urls')),
    url(r'^chart/', include('benchmark.chart.urls')),

    url(r'^avatar/', include('avatar.urls')),

    url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),

    url(r'^test/400/$', TemplateView.as_view(template_name='400.html'), name='test-400'),
    url(r'^test/500/$', test500, name='test-500'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
