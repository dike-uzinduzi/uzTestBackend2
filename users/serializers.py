from django.contrib.auth import get_user_model
from django.db.models import Q
from djoser.serializers import UserCreateSerializer, UserSerializer as BaseUserSerializer, TokenCreateSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils import timezone

User = get_user_model()


# ## 1. Serializer for CREATING a New User ##
class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Handles the creation of a new user during registration.
    """
    dob = serializers.DateField(source='date_of_birth', required=False, allow_null=True)

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'id', 'email', 'username', 'password', 'first_name', 'last_name',
            'gender', 'dob', 'is_artist', 'is_producer', 'stage_name', 'phone_number'
        )
    
    def create(self, validated_data):
        # This custom create method ensures all fields are passed to your model manager
        date_of_birth = validated_data.pop('date_of_birth', None)
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            gender=validated_data.get('gender'),
            date_of_birth=date_of_birth,
            phone_number=validated_data.get('phone_number'),
            stage_name=validated_data.get('stage_name'),
            is_artist=validated_data.get('is_artist', False),
            is_producer=validated_data.get('is_producer', False)
        )
        return user


# ## 2. Serializer for UPDATING a User's Profile ##
class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Handles partial updates to a user's own profile after they have logged in.
    """
    class Meta:
        model = User
        fields = [
            # Personal Info
            'first_name', 'last_name', 'gender', 'date_of_birth',
            # Contact & Location
            'phone_number', 'whatsapp_number', 'address',
            'national_id_number', 'citizenship', 'country_of_residence',
            # Media (File Uploads)
            'profile_pic', 'cover_photo',
            # Roles & Artist Info
            'is_artist', 'is_producer', 'stage_name', 'genre','is_fan'
        ]
        # NOTE: 'is_fan' was removed because it is not a field in the User model.


# ## 3. Serializer for DISPLAYING User Data (e.g., on /users/me/) ##
class CustomUserSerializer(BaseUserSerializer):
    """
    Safely displays user data, computing the user's role on the fly.
    """
    role = serializers.SerializerMethodField(read_only=True)

    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'role', 'is_active', 'is_artist', 'is_producer', 'is_staff','is_fan',
            'profile_pic', 'cover_photo', 'stage_name', 'genre',
            'phone_number', 'whatsapp_number', 'date_of_birth', 'date_joined', 'last_login'
        )
        read_only_fields = ('role', 'date_joined', 'last_login')
        # NOTE: 'is_fan' was removed. The get_role method correctly determines this status.

    def get_role(self, obj):
        if obj.is_superuser or obj.is_staff:
            return 'admin'
        if obj.is_artist:
            return 'artist'
        if obj.is_producer:
            return 'producer'
        if obj.is_fan:
            return 'fan'
        else:
            return 'guest'


# ## 4. Serializer for JWT Token Creation (Login) ##
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Adds a custom 'is_new_user' flag to the JWT token on first login
    and updates the user's 'last_login' timestamp.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['is_new_user'] = user.last_login is None
        token['username'] = user.username
        return token

    def validate(self, attrs):
        # This is the standard validation that checks username/password
        data = super().validate(attrs)

        # After a successful validation, `self.user` is the authenticated user.
        # We can now update their last_login timestamp.
        if self.user:
            self.user.last_login = timezone.now()
            self.user.save(update_fields=['last_login'])

        return data