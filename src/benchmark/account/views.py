from django.shortcuts import render, redirect
from django.contrib.auth.views import login
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy

from benchmark.account import forms
from benchmark.account.models import Account
from benchmark.utils.various import User
from benchmark.account.backends.hmac import ActivationBackend


class LoginView(TemplateView):
    template_name = 'account/login.html'
    form = forms.LoginForm()

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect('home')

        self.form = forms.LoginForm(request.POST or None)
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        redirect_to = self.request.GET.get('next', 'home')
        context['form'] = forms.LoginForm(initial={'next_': redirect_to})

        return context

    def post(self, request):
        redirect_to = self.request.POST.get('next_', 'home')
        if self.form.is_valid():
            login(request, request.user)
            return redirect(redirect_to)

        return self.get(request)


class AccountActivationView(FormView, ActivationBackend):
    """Activate user account by activation code and set a new password for user."""
    template_name = 'account/activation.html'
    form_class = forms.AccountActivationForm

    def dispatch(self, *args, **kwargs):
        activation_key = kwargs.get('activation_key')

        username = self.validate_key(activation_key)

        if username is not None:
            self.user = self.get_user(username)
            if self.user is not None:
                return super(AccountActivationView, self).dispatch(*args, **kwargs)

        return redirect('/')

    def form_valid(self, form):
        # Activate user - change his password and set to active
        user = self.user

        user.set_password(form.cleaned_data["password1"])
        user.is_active = True

        user.save()

        return render(self.request, 'account/activation-done.html', {})


class ForgotPasswordActivationView(FormView, ActivationBackend):
    template_name = 'account/change-password.html'
    form_class = forms.AccountActivationForm

    def dispatch(self, *args, **kwargs):
        activation_key = kwargs.get('activation_key')

        email = self.validate_key(activation_key)

        if email is not None:
            self.user = User.objects.get(email=email)
            if self.user is not None:
                return super(ForgotPasswordActivationView, self).dispatch(*args, **kwargs)

        return redirect('/')

    def form_valid(self, form):
        # Activate user - change his password and set to active
        user = self.user

        user.set_password(form.cleaned_data["password1"])
        user.is_active = True

        user.save()

        return render(self.request, 'account/change-password-done.html', {})


@method_decorator(login_required, name='dispatch')
class ProfileView(FormView):
    template_name = 'account/profile.html'
    form_class = forms.ChangePasswordForm

    def form_valid(self, form):
        # Change user password
        user = self.request.user

        user.set_password(form.cleaned_data["password1"])
        user.is_active = True

        user.save()

        return render(self.request, 'account/change-password-done.html', {})

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        account = Account.objects.get(user=self.request.user)
        if self.request.user.account.role == 2:
            context['agency_list'] = account.agency.all()
        return context

class ForgotPasswordView(FormView):
    template_name = 'account/forgot-password.html'
    form_class = forms.PasswordForgotRequestForm

    def form_valid(self, form):
        return render(self.request, 'account/forgot-password-done.html', {})


class AgencyView(FormView):
    template_name = 'account/agency_edit.html'
    form_class = forms.AgencyForm

    def form_valid(self, form):
        form.instance.save()

        return super().form_save(form)
