import uuid
from django.db import models
from django.conf import settings

class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Album(models.Model):
    artist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='albums')
    title = models.CharField(max_length=255)
    release_date = models.DateField()
    genre = models.ForeignKey(Genre, null=True, blank=True, on_delete=models.SET_NULL)
    cover_art = models.ImageField(upload_to='albums/covers/')
    description = models.TextField()
    track_count = models.PositiveIntegerField(default=0)
    copyright_info = models.TextField(blank=True, null=True)
    publisher = models.CharField(max_length=255, blank=True, null=True)
    credits = models.TextField(blank=True, null=True)
    affiliation = models.CharField(max_length=255, blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def update_track_count(self):
        self.track_count = self.tracks.count()
        self.save()

    def update_duration(self):
        total_duration = self.tracks.aggregate(total_duration=models.Sum('duration'))['total_duration']
        self.duration = total_duration if total_duration else None
        self.save()
  
    @property
    def total_bids(self):
        return self.activities.exclude(bid_amount__isnull=True).count()

    @property
    def current_supporters(self):
        return self.activities.filter(bid_amount__isnull=False).values('user').distinct().count()

class AlbumActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='album_activities')
    album = models.ForeignKey('Album', on_delete=models.CASCADE, related_name='activities')
    liked = models.BooleanField(default=False)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bid_date = models.DateTimeField(auto_now_add=True)
    currency = models.CharField(max_length=3, choices=[('USD', 'USD'), ('ZWL', 'ZWL')])
   # amount_supported = models.DecimalField(max_digits=10, decimal_places=2)
    plaque_count = models.PositiveBigIntegerField(default=0)
    amount_supported = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ('user', 'album')

    def __str__(self):
        return f"{self.user.username} on {self.album.title} (Liked: {self.liked}, Bid: {self.bid_amount})"

class Track(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='tracks')
    title = models.CharField(max_length=255)
    duration = models.DurationField()
#audio_file = models.FileField(null=True, upload_to='albums/tracks/')
    track_number = models.IntegerField(null=True, blank=True)
    featured_artists = models.CharField(max_length=255, blank=True, null=True)
    track_art = models.ImageField(upload_to='albums/tracks/art/', blank=True, null=True)
    track_description = models.TextField(blank=True, null=True)
    special_credits = models.TextField(blank=True, null=True)
    backing_vocals = models.CharField(max_length=255, blank=True, null=True)
    instrumentation = models.CharField(max_length=255, blank=True, null=True)
    release_date = models.DateField(null=True, blank=True)
    producer = models.CharField(max_length=255, blank=True, null=True)
    mastering_engineer = models.CharField(max_length=255, blank=True, null=True)
    mixing_engineer = models.CharField(max_length=255, blank=True, null=True)
    writer = models.CharField(max_length=255, blank=True, null=True)
    is_published = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['track_number']
        unique_together = ('album', 'track_number')

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
    hash_key = models.CharField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.hash_key:
            self.hash_key = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.plaque_type} Plaque - Hash: {self.hash_key}"
    



class PlaquePurchase(models.Model):
    plaque = models.OneToOneField(Plaque, on_delete=models.CASCADE, related_name='purchase_details')
    fan = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchases')
    album_supported = models.ForeignKey('Album', on_delete=models.CASCADE, related_name='plaque_purchases', null=True)
    hash_key = models.CharField(max_length=100, unique=True)
    purchase_date = models.DateField(auto_now_add=True)
    contribution_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, default='pending')
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    transaction_id = models.CharField(max_length=100)

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

