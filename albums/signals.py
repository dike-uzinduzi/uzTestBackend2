from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Track

@receiver([post_save,post_delete], sender=Track)
def update_album_duration(sender, instance, **kwargs):
    """
    Signal to update the album's duration when a track is saved or deleted.
    """
    if instance.album:
        instance.album.update_duration()
        instance.album.save()

@receiver([post_save, post_delete], sender=Track)
def update_album_track_count(sender, instance, **kwargs):
    """
    Signal to update the album's track count when a track is saved or deleted.
    """
    if instance.album:
        instance.album.update_track_count()
        instance.album.save()
