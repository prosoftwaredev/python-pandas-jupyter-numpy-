from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.conf import settings

from benchmark.utils.kms import string_or_b64kms


class Command(BaseCommand):
    help = (
        'Creates new superuser with password provided without any interactive '
        'input. Resets the password for existing user. Password may be either '
        'cleartext value or KMS-encrypted BASE64 stuff'
    )

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('password', type=str)

    def handle(self, *args, **kwargs):
        user, created = get_user_model().objects.get_or_create(
            username=kwargs['username']
        )

        user.set_password(string_or_b64kms(kwargs['password']))
        user.is_superuser = True
        user.email = kwargs['username']
        user.is_staff = True
        user.save()

        logging_data = {
            'DATABASE_ENGINE': settings.DATABASES['default']['ENGINE'],
            'DATABASE_NAME': settings.DATABASES['default']['NAME'],
            'DATABASE_USER': settings.DATABASES['default']['USER'],
            'DATABASE_HOST': settings.DATABASES['default']['HOST'],
            'DATABASE_PORT': settings.DATABASES['default']['PORT']
        }

        self.stdout.write('==========\n')
        self.stdout.write(str(logging_data))
        self.stdout.write('==========\n')

        if created:
            self.stdout.write("Complete, user created\n")
        else:
            self.stdout.write("Complete, user password updated\n")
        return
