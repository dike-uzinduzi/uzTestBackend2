from rest_framework import serializers
from .models import Artist

class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ['user', 'stage_name', 'genre', 'profile_pic', 'cover_photo']  # Add fields you want to expose
