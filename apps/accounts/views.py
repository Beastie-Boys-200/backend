import os
from urllib.parse import urlparse
from django.conf import settings
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UpdateProfileSerializer, ChangePasswordSerializer, SetPasswordSerializer, UserSerializer

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_path = '/auth/google/callback'
    permission_classes = [AllowAny]
    authentication_classes = []

    def _get_allowed_frontend_urls(self):
        frontend_urls_str = os.environ.get('FRONTEND_URLS', settings.FRONTEND_URL)
        return [url.strip() for url in frontend_urls_str.split(',') if url.strip()]

    def _extract_frontend_url_from_request(self):
        frontend_url = self.request.headers.get('X-Frontend-URL')
        if not frontend_url:
            referer = self.request.headers.get('Referer') or self.request.headers.get('Origin')
            if referer:
                parsed = urlparse(referer)
                frontend_url = f"{parsed.scheme}://{parsed.netloc}"
        return frontend_url

    @property
    def callback_url(self):
        allowed_urls = self._get_allowed_frontend_urls()
        frontend_url = self._extract_frontend_url_from_request()
        if frontend_url and frontend_url in allowed_urls:
            return f"{frontend_url}{self.callback_path}"
        return f"{allowed_urls[0]}{self.callback_path}"

    def get_response(self):
        serializer_class = self.get_response_serializer()
        if getattr(settings, 'REST_AUTH', {}).get('USE_JWT', False):
            from dj_rest_auth.jwt_auth import set_jwt_cookies
            from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

            refresh = TokenObtainPairSerializer.get_token(self.user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            data = {
                'user': self.user,
                'access': access_token,
                'refresh': refresh_token,
            }

            serializer = serializer_class(
                instance=data,
                context=self.get_serializer_context(),
            )
            response = Response(serializer.data, status=status.HTTP_200_OK)

            # Set httpOnly cookies
            set_jwt_cookies(response, access_token, refresh_token)

            return response
        else:
            return super().get_response()

class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            user_serializer = UserSerializer(request.user)
            return Response(user_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SetPasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password set successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
