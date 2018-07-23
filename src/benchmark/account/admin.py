from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.conf.urls import url
from django.utils.html import format_html
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from benchmark.account.models import Account, Agency
from benchmark.account.forms import AccountUserCreationForm
from benchmark.utils.various import User


admin.site.unregister(User)

@admin.register(User)
class UserAdmin(UserAdmin):
    add_form = AccountUserCreationForm

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_active',
        'user_actions'
    )

    readonly_fields = (
        'id',
        'actions',
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'role'),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form_class = super().get_form(request=request, obj=obj, **kwargs)
        form_class.request = request

        return form_class

    def get_urls(self):
        urls = super(UserAdmin, self).get_urls()
        custom_urls = [
            url(
                r'^(?P<user_id>.+)/send_activation/$',
                self.admin_site.admin_view(self.send_activation),
                name='user-send-activation-email',
            ),
        ]
        return custom_urls + urls

    def response_add(self, request, obj, post_url_continue="../%s/"):
        if '_continue' not in request.POST:
            self.message_user(
                request,
                f'New user successfully created and activation link sent to {obj.email}!'
            )
            return HttpResponseRedirect(reverse('admin:auth_user_changelist'))
        else:
            return super(MyModelAdmin, self).response_add(request, obj, post_url_continue)

    def send_activation(self, request, user_id, *args, **kwargs):
        # Send activation email with a link for a particular user

        user = self.get_object(request, user_id)

        try:
            user.account.send_activation_email(request)
            activation_key = user.account.get_activation_key(user)
            self.message_user(
                request,
                f'Activation link successfully sent to {user.email}!'
            )
        except Exception as e:
            self.message_user(
                request,
                f'Something went wrong while sending activation link to {user.email}',
                level=messages.ERROR
            )

        url = reverse(
            'admin:auth_user_changelist',
            current_app=self.admin_site.name,
        )

        return HttpResponseRedirect(url)

    def user_actions(self, obj):
        if not obj.is_active:
            return format_html(
                '<a class="button" href="{}">Send New Activation Email</a>',
                reverse('admin:user-send-activation-email', args=[obj.pk])
            )

    user_actions.short_description = 'Actions'
    user_actions.allow_tags = True


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    date_heirarchy = (
        'modified',
    )
    list_display = (
        'id',
        'user',
        'role',
    )
    readonly_fields = (
        'id',
    )
    list_select_related = (
        'user',
    )


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    date_heirarchy = (
        'modified',
    )
    list_display = (
        'id',
        'name',
        'code',
        'description'
    )
    readonly_fields = (
        'id',
    )
