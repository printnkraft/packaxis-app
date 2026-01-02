from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
import os


class Command(BaseCommand):
    help = 'Set up Google OAuth application for social login'

    def add_arguments(self, parser):
        parser.add_argument(
            '--client-id',
            type=str,
            help='Google OAuth Client ID',
            default=os.environ.get('GOOGLE_OAUTH_CLIENT_ID', '')
        )
        parser.add_argument(
            '--client-secret',
            type=str,
            help='Google OAuth Client Secret',
            default=os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET', '')
        )

    def handle(self, *args, **options):
        client_id = options['client_id']
        client_secret = options['client_secret']

        if not client_id or not client_secret:
            self.stdout.write(
                self.style.WARNING(
                    'Google OAuth credentials not provided. '
                    'Set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET environment variables. '
                    'Social login will be disabled.'
                )
            )
            return

        # Get or create the current site
        try:
            site = Site.objects.get_current()
        except Site.DoesNotExist:
            site = Site.objects.create(domain='packaxis.ca', name='PackAxis')
            self.stdout.write(self.style.SUCCESS(f'Created site: {site.domain}'))

        # Get or create Google OAuth app
        app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google',
                'client_id': client_id,
                'secret': client_secret,
            }
        )

        if created:
            app.sites.add(site)
            self.stdout.write(
                self.style.SUCCESS(f'Google OAuth app created with client_id: {client_id[:10]}...')
            )
        else:
            # Update existing app
            app.client_id = client_id
            app.secret = client_secret
            app.save()
            if site not in app.sites.all():
                app.sites.add(site)
            self.stdout.write(
                self.style.SUCCESS(f'Google OAuth app updated with client_id: {client_id[:10]}...')
            )
