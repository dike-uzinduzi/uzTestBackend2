from rest_framework import serializers
from django.shortcuts import get_object_or_404
from .models import Album, Plaque, Track, PlaquePurchase


class PlaquePurchaseCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaquePurchase
        fields = ['id']

class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ['id', 'title', 'duration', 'track_number', 'featured_artists']

class AlbumSerializer(serializers.ModelSerializer):
    artist_name = serializers.CharField(source='artist.first_name', read_only=True)  # Access the stage_name field
    genre_name = serializers.CharField(source='genre.name', read_only=True)  # Ensure this points to the genre model correctly

    class Meta:
        model = Album
        fields = [
            'id',
            'title',
            'release_date',
            'genre_name',
            'cover_art',
            'description',
            'track_count',
            'copyright_info',
            'publisher',
            'credits',
            'artist_name'  # Include artist_name in the response
        ]
class SupportAlbumSerializer(serializers.Serializer):
    album_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def create(self, validated_data):
        user = self.context['request'].user
        album = get_object_or_404(Album, id=validated_data['album_id'])
        amount = validated_data['amount']

        # Create a purchase record
        purchase = PlaquePurchase.objects.create(
            fan=user,  # Assuming the user is a fan
            album=album,
            amount=amount
        )

        # Determine the plaque type based on the amount
        if 1 <= amount <= 50:
            plaque_type = 'thank_you'
        elif 51 <= amount <= 100:
            plaque_type = 'wood'
        elif 101 <= amount <= 300:
            plaque_type = 'ruby'
        elif 301 <= amount <= 500:
            plaque_type = 'bronze'
        elif 501 <= amount <= 700:
            plaque_type = 'silver'
        elif 701 <= amount <= 900:
            plaque_type = 'gold'
        else:
            plaque_type = 'emerald'

        # Create the plaque
        plaque = Plaque.objects.create(
            plaque_type=plaque_type
        )

        # Link the plaque to the purchase
        purchase.plaque = plaque
        purchase.save()

        return purchase

    def to_representation(self, instance):
        # Customize the response to include plaque details
        response = super().to_representation(instance)
        response['plaque'] = {
            'plaque_type': instance.plaque.plaque_type,
            'hash_key': instance.plaque.hash_key
        }
        return response
