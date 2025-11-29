from django.urls import path
from .views import GoogleLogin, UpdateProfileView, ChangePasswordView, SetPasswordView

urlpatterns = [
    path('google/', GoogleLogin.as_view(), name='google_login'),
    path('update-profile/', UpdateProfileView.as_view(), name='update_profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('set-password/', SetPasswordView.as_view(), name='set_password'),
]
