import operator

from functools import reduce

from django.db import models
from django.utils.functional import cached_property
from django.contrib.sites.shortcuts import get_current_site

from benchmark.utils.models import BaseUUIDModel
from benchmark.utils.various import User
from benchmark.utils.email import EmailService
from benchmark.account.backends.hmac import ActivationBackend


class Agency(BaseUUIDModel):
    name = models.CharField(max_length=60, help_text='Name')
    code = models.CharField(max_length=20, help_text='Short code')

    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Agency name'
        verbose_name_plural = 'Agencies'

    def __str__(self):
        return self.code

    @staticmethod
    def update_from_data(agencies):
        normalized = {a['Agency name']: a['Department'] for a in agencies}

        agency_names = set(a for a, d in normalized.items())

        query = reduce(operator.or_, (models.Q(name__iexact=item) for item in agency_names))
        existing_agencies = set(Agency.objects.filter(query).values_list('name', flat=True))

        new_agencies = agency_names - existing_agencies

        print(new_agencies)

        for new_agency in new_agencies:
            Agency.objects.create(
                name=normalized[new_agency],
                code=new_agency
            )


class Account(BaseUUIDModel, ActivationBackend):
    """User account followed by role"""
    ROLE_FINANCE_ADMIN, ROLE_AGENCY_USER = range(1, 3)
    ROLE_CHOICES = (
        (ROLE_FINANCE_ADMIN, 'Finance admin'),
        (ROLE_AGENCY_USER, 'Agency user')
    )

    user = models.OneToOneField(User, related_name='account', help_text='User')
    role = models.SmallIntegerField(choices=ROLE_CHOICES, help_text='Role')

    agency = models.ManyToManyField(Agency, blank=True)

    class Meta:
        verbose_name = 'User Account'
        verbose_name_plural = 'User Accounts'

    def __str__(self):
        return f"{self.user} at {self.role}"

    @property
    def is_finance_admin(self):
        return self.role == Account.ROLE_FINANCE_ADMIN

    def send_activation_email(self, request):
        activation_key = self.get_activation_key(user=self.user)

        EmailService().send_messages(
            subject='Invitation to be a member',
            template='email/account/activation.html',
            to_emails=[self.user.email],
            context={
                'activation_key': activation_key
            },
        )

    def send_confirmation_email(self, user):
        activation_key = self.get_activation_key(user=user)

        EmailService().send_messages(
            subject='Reset Password',
            template='email/account/forgot-password.html',
            to_emails=[user.email],
            context={
                'activation_key': activation_key
            },
        )