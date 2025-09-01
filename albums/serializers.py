from rest_framework import serializers
from django.shortcuts import get_object_or_404
from .models import Album, Plaque, Track, PlaquePurchase, Genre
from django.db.models import Count, Q
import uuid

class PlaquePurchaseCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaquePurchase
        fields = ['id']

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'

class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = '__all__'

class AlbumSerializer(serializers.ModelSerializer):
    artist_name = serializers.CharField(source='artist.first_name', read_only=True)
    genre_name = serializers.CharField(source='genre.name', read_only=True)
    stage_name = serializers.CharField(source='artist.stage_name')
    
    class Meta:
        model = Album
        fields = '__all__'

class SupportAlbumSerializer(serializers.Serializer):
    album_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    def create(self, validated_data):
        user = self.context['request'].user
        album = get_object_or_404(Album, id=validated_data['album_id'])
        amount = validated_data['amount']
        
        purchase = PlaquePurchase.objects.create(
            fan=user,
            album_supported=album,
            contribution_amount=amount,
            hash_key=str(uuid.uuid4()),
            transaction_id=str(uuid.uuid4())
        )
        
        plaque = Plaque.objects.create(
            plaque_type=purchase.get_plaque_type(amount)
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

class PlaquePurchaseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaquePurchase
        fields = '__all__'


class UserPlaqueStatsSerializer(serializers.Serializer):
    purchased = serializers.IntegerField(read_only=True)
    pending = serializers.IntegerField(read_only=True)
    albums_supported = serializers.IntegerField(read_only=True)
    
    def to_representation(self, instance):
        user = self.context['request'].user
        purchased = PlaquePurchase.objects.filter(fan=user, payment_status='completed').count()
        pending = PlaquePurchase.objects.filter(fan=user, payment_status='pending').count()
        albums_supported = PlaquePurchase.objects.filter(fan=user).values('album_supported').distinct().count()
        
        return {
            'purchased': purchased,
            'pending': pending,
            'albums_supported': albums_supported
        }