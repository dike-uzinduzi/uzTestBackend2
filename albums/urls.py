from django.urls import path
from .views import (
    LatestAlbumsView, AlbumDetailView, AllAlbumsView, UserPlaquePurchaseCountView,
    AllTracksView, TrackDetailView, AlbumTracksView, AlbumStatisticsView
)

urlpatterns = [
    path('plaques-count/', UserPlaquePurchaseCountView.as_view(), name='plaques-count'),
    path('albums/', AllAlbumsView.as_view(), name='all-albums'),
    path('latest-albums/', LatestAlbumsView.as_view(), name='latest-albums'),
    path('albums/<int:id>/', AlbumDetailView.as_view(), name='album-detail'),
    path('albums/<int:id>/statistics/', AlbumStatisticsView.as_view(), name='album-statistics'),
    path('tracks/', AllTracksView.as_view(), name='all-tracks'),
    path('tracks/<int:id>/', TrackDetailView.as_view(), name='track-detail'),
    path('albums/<int:id>/tracks/', AlbumTracksView.as_view(), name='album-tracks'),
]
