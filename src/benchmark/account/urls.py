from django.contrib.auth.views import logout
from django.conf.urls import url

from benchmark.account import views


urlpatterns = [
    url(r'^login/$', views.LoginView.as_view(), name='account-login'),
    url(r'^logout/$', logout, {'next_page': '/account/login/'}, name='account-logout'),
    url(r'^forgot-password/$', views.ForgotPasswordView.as_view(), name='forgot-password'),
    url(r'^profile/$', views.ProfileView.as_view(), name='account-profile'),
    url(
        r'^activation/(?P<activation_key>[-:\w]+)/$',
        views.AccountActivationView.as_view(),
        name="account-activation"
    ),
    url(
        r'^forgot-password/(?P<activation_key>[-:\w]+)/$',
        views.ForgotPasswordActivationView.as_view(),
        name="forgot-password-activation"
    ),
    url(r'^agency/$', views.AgencyView.as_view(), name='agency-create'),
]
