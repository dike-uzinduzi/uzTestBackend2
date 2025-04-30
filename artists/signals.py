from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import UserAccount
from .models import Artist

@receiver(post_save, sender=UserAccount)
def create_or_update_artist(sender, instance, created, **kwargs):
    # Check if the user is an artist
    if instance.is_artist:
        # If the artist already exists, update the fields
        Artist.objects.update_or_create(
            user=instance,
            defaults={
                'stage_name': instance.stage_name,
                'genre': instance.genre,
                'profile_pic': instance.profile_pic,
                'cover_photo': instance.cover_photo
            }
        )
    else:
        # If the user is no longer an artist, delete the related artist record
        Artist.objects.filter(user=instance).delete()
