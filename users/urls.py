from django.urls import path, re_path
from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
    LogoutView,
    UserProfileUpdateView,
    CustomProviderAuthView,
)

urlpatterns = [
    # JWT Authentication with Cookies
    path('jwt/create/', CustomTokenObtainPairView.as_view(), name='jwt-create'),
    path('jwt/refresh/', CustomTokenRefreshView.as_view(), name='jwt-refresh'),
    path('jwt/verify/', CustomTokenVerifyView.as_view(), name='jwt-verify'),

    # User Profile
    path('profile/update/', UserProfileUpdateView.as_view(), name='profile-update'),
    
    # Social Authentication
    re_path(
        r'^o/(?P<provider>\S+)/$',
        CustomProviderAuthView.as_view(),
        name='provider-auth'
    ),
    
    # Logout
    path('logout/', LogoutView.as_view(), name='logout'),
]