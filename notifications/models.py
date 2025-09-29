from django.db import models
from django.conf import settings

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # A key to identify the purpose of the notification, e.g., 'incomplete-profile'
    notification_key = models.CharField(max_length=100, blank=True, null=True, db_index=True)

    def __str__(self):
        return f'Notification for {self.user.username}: {self.title}'