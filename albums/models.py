import uuid
from django.db import models
from django.conf import settings

class Genre(models.Model):
    # genre choices
    GENRE_CHOICES = [
        ('jiti', 'Jiti'),
        ('sungura', 'Sungura'),
        ('jazz', 'Jazz'),
        ('hip_hop', 'Hip-Hop'),
        ('gospel', 'Gospel'),
        ('reggae', 'Reggae'),
        ('zimdancehall', 'Zimdancehall'),
        ('mbira', 'Mbira'),
        ('dancehall', 'Dancehall'),
        ('trap', 'Trap'),
        
    ]

    name = models.CharField(max_length=255, choices=GENRE_CHOICES, unique=True)

    def __str__(self):
        return self.name

    
class Album(models.Model):
    artist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='albums')
    title = models.CharField(max_length=255)
    release_date = models.DateField()
    genre = models.ForeignKey(Genre, null=True, blank=True, on_delete=models.SET_NULL)
    cover_art = models.ImageField(upload_to='albums/covers/')
    description = models.TextField()
    track_count = models.IntegerField(blank=True, null=True)
    copyright_info = models.TextField(blank=True, null=True)
    publisher = models.CharField(max_length=255, blank=True, null=True)
    credits = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title
    
class Track(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='tracks')
    title = models.CharField(max_length=255)
    duration = models.DurationField()  # Use DurationField to store track length
    audio_file = models.FileField(null=True, upload_to='albums/tracks/')
    track_number = models.IntegerField(null=True, blank=True)
    featured_artists = models.CharField(max_length=255, blank=True, null=True)  # Consider ManyToMany if needed
    track_art = models.ImageField(upload_to='albums/tracks/art/', blank=True, null=True)
    track_credits = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['track_number']

    def __str__(self):
        return f"{self.track_number}. {self.title}" if self.track_number else f"Untitled Track: {self.title}"

class Plaque(models.Model):
    PLAQUE_TYPE_CHOICES = [
        ('thank_you', 'Thank You'),
        ('wood', 'Wood'),
        ('ruby', 'Ruby'),
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('emerald', 'Emerald'),
    ]

    plaque_type = models.CharField(max_length=10, choices=PLAQUE_TYPE_CHOICES, default='thank_you')
    hash_key = models.CharField(max_length=100, unique=True, blank=True)  # Make hash_key blank initially

    def save(self, *args, **kwargs):
        # Generate a unique hash key if it doesn't exist
        if not self.hash_key:
            self.hash_key = str(uuid.uuid4())  # Generate a unique UUID as the hash key
        super().save(*args, **kwargs)  # Call the original save method

    def __str__(self):
        return f"{self.plaque_type} Plaque - Hash: {self.hash_key}"
    
    
class PlaquePurchase(models.Model):
    plaque = models.OneToOneField(Plaque, on_delete=models.CASCADE, related_name='purchase_details')
    fan = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchases')
    album_supported = models.ForeignKey('Album', on_delete=models.CASCADE, related_name='plaque_purchases', null=True)
    hash_key = models.CharField(max_length=100, unique=True)
    purchase_date = models.DateField(auto_now_add=True)
    contribution_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Payment fields
    payment_status = models.CharField(max_length=20, default='pending')  # Payment status
    payment_method = models.CharField(max_length=50, blank=True, null=True)  # Payment method
    transaction_id = models.CharField(max_length=100, blank=True, null=True)  # Transaction ID from payment gateway

    def save(self, *args, **kwargs):
        self.plaque.plaque_type = self.get_plaque_type(self.contribution_amount)
        self.plaque.save()
        super().save(*args, **kwargs)

    def get_plaque_type(self, amount):
        if amount < 51:
            return 'thank_you'
        elif 51 <= amount <= 100:
            return 'wood'
        elif 101 <= amount <= 300:
            return 'ruby'
        elif 301 <= amount <= 500:
            return 'bronze'
        elif 501 <= amount <= 700:
            return 'silver'
        elif 701 <= amount <= 900:
            return 'gold'
        else:
            return 'emerald'

    def __str__(self):
        return f"Purchase Details for {self.plaque} - Hash Key: {self.hash_key}"
