from rest_framework import serializers
from .models import UserAccount

class UserAccountUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = [
            'first_name', 'last_name', 'email', 'address',
            'phone_number', 'whatsapp_number', 'date_of_birth',
            'national_id_number', 'citizenship', 'country_of_residence',
            'profile_pic', 'cover_photo', 'stage_name', 'genre'
        ]

    def validate(self, data):
        # Ensure artist fields are validated only for artists
        if self.instance.is_artist:
            if 'stage_name' in data and not data['stage_name']:
                raise serializers.ValidationError("Stage name cannot be empty.")
            if 'genre' in data and not data['genre']:
                raise serializers.ValidationError("Genre cannot be empty.")
        return data
