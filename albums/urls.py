from django.urls import path
from .views import  LatestAlbumsView, AlbumDetailView,AllAlbumsView,UserPlaquePurchaseCountView

urlpatterns = [
     path('plaques-count/', UserPlaquePurchaseCountView.as_view(), name='plaques-count'),
     path('albums/', AllAlbumsView.as_view(), name='all-albums'),  # URL for getting all albums
     path('latest-albums/', LatestAlbumsView.as_view(), name='latest-albums'),
    path('albums/<int:id>/', AlbumDetailView.as_view(), name='album-detail'),
    
]
