import os
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

class Command(BaseCommand):
    help = 'Set up Google OAuth2 application in the database'

    def handle(self, *args, **options):
        client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
        client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '')

        if not client_id or not client_secret:
            self.stdout.write(
                self.style.WARNING(
                    'GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not set in environment variables.'
                )
            )
            return

        site = Site.objects.get_current()

        # Создание или обновление Google SocialApp
        social_app, created = SocialApp.objects.update_or_create(
            provider='google',
            defaults={
                'name': 'Google OAuth2',
                'client_id': client_id,
                'secret': client_secret,
            }
        )

        if site not in social_app.sites.all():
            social_app.sites.add(site)

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created Google OAuth2 app with client_id: {client_id[:20]}...'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated Google OAuth2 app with client_id: {client_id[:20]}...'
                )
            )
