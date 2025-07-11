from rest_framework import serializers
from django.shortcuts import get_object_or_404
from .models import Album, Plaque, Track, PlaquePurchase,Genre


class PlaquePurchaseCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaquePurchase
        fields = ['id']

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model=Genre
        fields='__all__'
        
class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = '__all__'
class AlbumSerializer(serializers.ModelSerializer):
    
    artist_name = serializers.CharField(source='artist.first_name', read_only=True)  # Access the stage_name field
    genre_name = serializers.CharField(source='genre.name', read_only=True)  # Ensure this points to the genre model correctly
   # current_supporters = serializers.IntegerField(source='current_supporters', read_only=True)
    class Meta:
        model = Album
        fields='__all__'

class SupportAlbumSerializer(serializers.Serializer):
    album_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def create(self, validated_data):
        user = self.context['request'].user
        album = get_object_or_404(Album, id=validated_data['album_id'])
        amount = validated_data['amount']

        
        purchase = PlaquePurchase.objects.create(
            fan=user,  
            album=album,
            amount=amount
        )

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

        
        plaque = Plaque.objects.create(
            plaque_type=plaque_type
        )

       
        purchase.plaque = plaque
        purchase.save()

        return purchase

    def to_representation(self, instance):
        
        response = super().to_representation(instance)
        response['plaque'] = {
            'plaque_type': instance.plaque.plaque_type,
            'hash_key': instance.plaque.hash_key
        }
        return response
    

class PlaqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plaque
        fields = ['id', 'plaque_type', 'hash_key']

class PlaquePurchaseSerializer(serializers.ModelSerializer):
    plaque = PlaqueSerializer(read_only=True)
    
    class Meta:
        model = PlaquePurchase
        fields = [
            'id', 'plaque', 'fan', 'album_supported', 'hash_key',
            'purchase_date', 'contribution_amount', 'payment_status',
            'payment_method', 'transaction_id'
        ]
        read_only_fields = ['hash_key', 'purchase_date']