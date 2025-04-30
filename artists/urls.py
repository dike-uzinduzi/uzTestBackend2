from django.urls import path
from .views import ArtistDashboardView

urlpatterns = [
    path('artist/dashboard/', ArtistDashboardView.as_view(), name='artist-dashboard'),
]
