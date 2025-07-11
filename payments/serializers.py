from rest_framework import serializers
from .models import Payment, PaymentLog

class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'reference_number', 'amount', 'currency', 'payment_method',
            'payment_reason', 'customer_email', 'customerPhoneNumber', 'customer_name',
            'status', 'payment_type', 'created_at', 'updated_at', 'completed_at',
            'album_title', 'artist_name', 'plaque_type', 'user_email'
        ]
        read_only_fields = ['id', 'reference_number', 'created_at', 'updated_at', 'completed_at']

class PaymentLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentLog
        fields = ['event_type', 'message', 'data', 'timestamp']
