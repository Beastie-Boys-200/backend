import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Create or update Django superuser from environment variables'

    def handle(self, *args, **options):
        User = get_user_model()

        # Чтение ENV переменных
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')
        first_name = os.environ.get('DJANGO_SUPERUSER_FIRST_NAME', 'Admin')
        last_name = os.environ.get('DJANGO_SUPERUSER_LAST_NAME', 'User')

        if not email or not password:
            self.stdout.write(
                self.style.WARNING(
                    'DJANGO_SUPERUSER_EMAIL or DJANGO_SUPERUSER_PASSWORD not set in environment variables. '
                    'Superuser creation skipped.'
                )
            )
            return

        try:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.first_name = first_name
            user.last_name = last_name
            user.is_staff = True
            user.is_superuser = True
            user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated superuser: {email}'
                )
            )
        except User.DoesNotExist:
            User.objects.create_superuser(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created superuser: {email}'
                )
            )
