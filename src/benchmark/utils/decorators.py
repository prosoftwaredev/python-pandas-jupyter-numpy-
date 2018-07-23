from django.contrib.auth.decorators import user_passes_test


def role_finance_admin_required(function=None, redirect_field_name=None, login_url=None):
    """
    Decorator for views that checks that the user is logged in and assigned with finance admin role.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.account.is_finance_admin,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
