from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

# Сигналы отключены - логика в CustomSocialAccountAdapter
