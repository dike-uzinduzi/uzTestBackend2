from django.contrib.auth import user_logged_in
from django.dispatch import receiver
from notifications.models import Notification # Import from your notifications app

@receiver(user_logged_in)
def check_profile_completeness(sender, request, user, **kwargs):
    """
    Checks user profile on login and creates notifications for missing info.
    """
    profile_warning_key = 'incomplete-profile'
    
    # First, remove any existing incomplete profile notifications for this user
    Notification.objects.filter(user=user, notification_key__startswith=profile_warning_key).delete()

    # Define the fields considered essential
    essential_fields = {
        'phone_number': 'Phone Number',
        'date_of_birth': 'Date of Birth',
        'address': 'Address',
    }

    # Create a new notification for each missing field
    for field_key, field_name in essential_fields.items():
        if not getattr(user, field_key, None):
            Notification.objects.create(
                user=user,
                title='Incomplete Profile',
                message=f'Please add your {field_name} to complete your profile.',
                notification_key=f'{profile_warning_key}-{field_key}'
            )