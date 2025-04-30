from rest_framework import status, generics,permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication  # Import JWT authentication
from .serializers import SupportAlbumSerializer, AlbumSerializer,PlaquePurchase
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Album

# View to get latest albums (accessible to all users)
class LatestAlbumsView(generics.ListAPIView):
    queryset = Album.objects.order_by('-release_date')[:10]  # Fetch latest 10 albums
    serializer_class = AlbumSerializer
    permission_classes = [permissions.AllowAny]  # Allow any user (authenticated or not)

# View to get album by ID (accessible to all users)
class AlbumDetailView(generics.RetrieveAPIView):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    lookup_field = 'id'  # Fetch the album by its ID
    permission_classes = [permissions.AllowAny]  # Allow any user (authenticated or not)
# View to get all albums (accessible to all users)
class AllAlbumsView(generics.ListAPIView):
    queryset = Album.objects.all()  # Fetch all albums
    serializer_class = AlbumSerializer
    permission_classes = [permissions.AllowAny]  # Allow any user (authenticated or not)

class UserPlaquePurchaseCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Get the number of plaques the logged-in user has purchased
        user = request.user
        plaque_count = PlaquePurchase.objects.filter(fan=user).count()
        
        # Return the count in the response
        return Response({'plaques_purchased': plaque_count})