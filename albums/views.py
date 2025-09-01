from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django.db import models
from .serializers import SupportAlbumSerializer, AlbumSerializer, TrackSerializer, GenreSerializer, PlaquePurchaseDetailSerializer, UserPlaqueStatsSerializer
from .models import Album, PlaquePurchase, AlbumActivity, Track, Genre

class LatestAlbumsView(generics.ListAPIView):
    queryset = Album.objects.order_by('-release_date')[:10]
    serializer_class = AlbumSerializer
    permission_classes = [permissions.AllowAny]

class AlbumDetailView(generics.RetrieveAPIView):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    lookup_field = 'id'
    permission_classes = [permissions.AllowAny]

class AllAlbumsView(generics.ListAPIView):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    permission_classes = [permissions.AllowAny]

class UserPlaquePurchaseCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        plaque_count = PlaquePurchase.objects.filter(fan=user).count()
        return Response({'plaques_purchased': plaque_count})

class UserPlaqueStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserPlaqueStatsSerializer
    
    def get(self, request):
        serializer = self.serializer_class(data={}, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

class AllPlaquePurchaseView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PlaquePurchaseDetailSerializer
    
    def get(self, request):
        user = request.user
        plaques = PlaquePurchase.objects.filter(fan=user)
        serializer = self.serializer_class(plaques, many=True)
        return Response(serializer.data)

class AllTracksView(generics.ListAPIView):
    queryset = Track.objects.all()
    serializer_class = TrackSerializer
    permission_classes = [permissions.AllowAny]

class AllGenreView(generics.ListAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [permissions.AllowAny]

class TrackDetailView(generics.RetrieveAPIView):
    queryset = Track.objects.all()
    serializer_class = TrackSerializer
    lookup_field = 'id'
    permission_classes = [permissions.AllowAny]

class AlbumTracksView(ListAPIView):
    serializer_class = TrackSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        album_id = self.kwargs['id']
        return Track.objects.filter(album_id=album_id, is_deleted=False)

class AlbumStatisticsView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, id):
        try:
            album = Album.objects.get(id=id)
            usd_activities = AlbumActivity.objects.filter(album=album, currency='USD')
            zig_activities = AlbumActivity.objects.filter(album=album, currency='ZWL')
            
            usd_total = usd_activities.aggregate(
                total=models.Sum('amount_supported')
            )['total'] or 0
            
            zig_total = zig_activities.aggregate(
                total=models.Sum('amount_supported')
            )['total'] or 0
            
            return Response({
                'usd_support': float(usd_total),
                'zig_support': float(zig_total),
                'total_bids': album.total_bids,
                'current_supporters': album.current_supporters
            })
        except Album.DoesNotExist:
            return Response({'error': 'Album not found'}, status=404)