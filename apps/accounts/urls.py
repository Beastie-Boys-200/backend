from django.urls import path
from .views import GoogleLogin, UpdateProfileView, ChangePasswordView

urlpatterns = [
    path('google/', GoogleLogin.as_view(), name='google_login'),
    path('update-profile/', UpdateProfileView.as_view(), name='update_profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
]
