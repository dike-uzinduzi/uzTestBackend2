from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin
)
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

class UserAccountManager(BaseUserManager):
    # --- UPDATED create_user method ---
    def create_user(self, email, username, password=None, **kwargs):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')

        email = self.normalize_email(email).lower()

        user = self.model(
            email=email,
            username=username,
            **kwargs
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    # --- UPDATED create_superuser method ---
    def create_superuser(self, email, username, password=None, **kwargs):
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_artist', False)

        if kwargs.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if kwargs.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        return self.create_user(email, username, password, **kwargs)

class UserAccount(AbstractBaseUser, PermissionsMixin):

    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    # Core Fields
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, max_length=255)
    username = models.CharField(max_length=255, unique=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True) 
    # Contact & Personal Info (Optional)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+263774556973'. Up to 15 digits allowed.")
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    whatsapp_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    national_id_number = models.CharField(max_length=100, null=True, blank=True)
    citizenship = models.CharField(max_length=50, null=True, blank=True)
    country_of_residence = models.CharField(max_length=50, null=True, blank=True)
    
    # Media
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    cover_photo = models.ImageField(upload_to='cover_photos/', null=True, blank=True)
    
    # Artist-specific fields
    stage_name = models.CharField(max_length=255, null=True, blank=True)
    genre = models.CharField(max_length=255, blank=True, null=True)
    is_artist = models.BooleanField(default=False)
    is_fan = models.BooleanField(default=False)
    is_producer = models.BooleanField(default=False)
    
    # Django Permissions & Status
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        # IMPROVED LOGIC: Fallback to username if not an artist or no stage name
        if self.is_artist and self.stage_name:
            return self.stage_name
        return self.username

    def save(self, *args, **kwargs):
        if not self.is_artist:
            self.stage_name = None
        super().save(*args, **kwargs)
