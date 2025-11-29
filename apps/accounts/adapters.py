from django.conf import settings
from django.contrib.auth import get_user_model
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class CustomAccountAdapter(DefaultAccountAdapter):
    def clean_email(self, email):
        email = super().clean_email(email)
        if User.objects.filter(email__iexact=email).exists():
            user = User.objects.get(email__iexact=email)
            if user.socialaccount_set.exists():
                provider = user.socialaccount_set.first().provider
                raise ValidationError(
                    f"An account with this email already exists. "
                    f"Please sign in using {provider.capitalize()} or use a different email."
                )
            else:
                raise ValidationError(
                    "An account with this email already exists. "
                    "Please use a different email or try logging in."
                )
        return email

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Автоподключение соц. аккаунта к существующему юзеру
        if sociallogin.is_existing:
            return

        email = sociallogin.email_addresses[0].email if sociallogin.email_addresses else None
        if not email:
            return

        try:
            with transaction.atomic():
                existing_user = User.objects.select_for_update().get(email__iexact=email)
                sociallogin.connect(request, existing_user)
                logger.info(f"Connected social account to existing user: {email}")
        except User.DoesNotExist:
            pass
        except IntegrityError as e:
            logger.error(f"IntegrityError during social login: {email}, error: {str(e)}")
            try:
                existing_user = User.objects.get(email__iexact=email)
                sociallogin.connect(request, existing_user)
                logger.info(f"Recovered and connected user: {email}")
            except Exception as retry_error:
                logger.error(f"Failed to recover: {str(retry_error)}")
                raise
        except Exception as e:
            logger.error(f"Unexpected error during pre_social_login: {str(e)}")
            raise

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        if not user.first_name and 'first_name' in data:
            user.first_name = data['first_name']
        if not user.last_name and 'last_name' in data:
            user.last_name = data['last_name']
        if not user.first_name and not user.last_name and 'name' in data:
            name_parts = data['name'].split(' ', 1)
            user.first_name = name_parts[0]
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        return user

    def is_auto_signup_allowed(self, request, sociallogin):
        return bool(sociallogin.email_addresses)

    def save_user(self, request, sociallogin, form=None):
        email = sociallogin.email_addresses[0].email if sociallogin.email_addresses else None
        if email:
            existing_user = User.objects.filter(email__iexact=email).first()
            if existing_user:
                logger.warning(f"save_user() caught duplicate for: {email}")
                sociallogin.connect(request, existing_user)
                return existing_user
        return super().save_user(request, sociallogin, form)
