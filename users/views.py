from django.conf import settings
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from djoser.social.views import ProviderAuthView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

# Import all the necessary custom serializers
from .serializers import (
    UserProfileUpdateSerializer,
    CustomTokenObtainPairSerializer
)

# --- Helper Function for Setting Cookies ---
def set_auth_cookies(response, access_token, refresh_token=None):
    response.set_cookie(
        key='access',
        value=access_token,
        max_age=settings.AUTH_COOKIE_MAX_AGE,
        path=settings.AUTH_COOKIE_PATH,
        secure=settings.AUTH_COOKIE_SECURE,
        httponly=settings.AUTH_COOKIE_HTTP_ONLY,
        samesite=settings.AUTH_COOKIE_SAMESITE
    )
    if refresh_token:
        response.set_cookie(
            key='refresh',
            value=refresh_token,
            max_age=settings.AUTH_COOKIE_MAX_AGE,
            path=settings.AUTH_COOKIE_PATH,
            secure=settings.AUTH_COOKIE_SECURE,
            httponly=settings.AUTH_COOKIE_HTTP_ONLY,
            samesite=settings.AUTH_COOKIE_SAMESITE
        )
    return response

# --- Authentication Views ---

class CustomTokenObtainPairView(TokenObtainPairView):
    """Handles user login and sets JWTs as HTTPOnly cookies."""
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')
            set_auth_cookies(response, access_token, refresh_token)
        return response

# ## ADD THIS VIEW ##
class CustomTokenRefreshView(TokenRefreshView):
    """Refreshes the access token using the refresh token from cookies."""
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh')
        if refresh_token:
            request.data['refresh'] = refresh_token
        
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access_token = response.data.get('access')
            set_auth_cookies(response, access_token) # Only the access token is re-set
        return response

# ## ADD THIS VIEW ##
class CustomTokenVerifyView(TokenVerifyView):
    """Verifies the access token from cookies."""
    def post(self, request, *args, **kwargs):
        access_token = request.COOKIES.get('access')
        if access_token:
            request.data['token'] = access_token
        return super().post(request, *args, **kwargs)

class CustomProviderAuthView(ProviderAuthView):
    """Handles social authentication and sets tokens as cookies."""
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')
            set_auth_cookies(response, access_token, refresh_token)
        return response

class LogoutView(APIView):
    """Handles user logout by deleting the authentication cookies."""
    permission_classes = [permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        response = Response({"detail": "Logout successful."}, status=status.HTTP_200_OK)
        response.delete_cookie('access')
        response.delete_cookie('refresh')
        return response

# --- Profile Management View ---

class UserProfileUpdateView(generics.UpdateAPIView):
    """Handles PATCH requests to update the logged-in user's profile."""
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user