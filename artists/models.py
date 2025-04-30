from django.db import models
from users.models import UserAccount 


class Artist(models.Model):
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    stage_name = models.CharField(max_length=255)
    genre = models.CharField(max_length=255, null=True, blank=True)
    profile_pic = models.ImageField(upload_to='artist_profile_pics/', null=True, blank=True)
    cover_photo = models.ImageField(upload_to='artist_cover_photos/', null=True, blank=True)
    
    def __str__(self):
        return self.stage_name
