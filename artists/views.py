from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Artist
from .serializers import ArtistSerializer

class ArtistDashboardView(APIView):
    def get(self, request, format=None):
        artist = Artist.objects.filter(user=request.user).first()  # Assuming you're querying based on the logged-in user
        if artist:
            serializer = ArtistSerializer(artist)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Artist not found"}, status=status.HTTP_404_NOT_FOUND)
