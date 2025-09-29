from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer

class NotificationListView(generics.ListAPIView):
    """
    Returns a list of notifications for the currently authenticated user.
    
    This view dynamically generates role-specific and profile-completeness
    warnings, and fetches any other persistent notifications from the database.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Returns the base queryset of persistent notifications for the user.
        """
        return self.request.user.notifications.filter(is_read=False).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        user = self.request.user
        dynamic_notifications = []
        temp_id_counter = -1

        def add_dynamic_notification(title, message):
            nonlocal temp_id_counter
            dynamic_notifications.append({
                'id': temp_id_counter,
                'title': title,
                'message': message,
                'is_read': False,
                'created_at': None 
            })
            temp_id_counter -= 1

        # --- Step 1: Check for role-specific issues ---

        # Check for an undefined role
        is_role_defined = any([user.is_artist, user.is_producer, user.is_staff, user.is_superuser, user.is_fan])
        
        if not is_role_defined:
            add_dynamic_notification(
                'Role Not Set', 
                'Please complete your profile to define your role as an Artist, Producer, or Fan.'
            )
        
        # Artist-specific checks
        if user.is_artist:
            if not user.stage_name:
                add_dynamic_notification(
                    'Artist Profile Incomplete',
                    'Please add your Stage Name to complete your artist profile.'
                )
            if not user.genre:
                 add_dynamic_notification(
                    'Artist Profile Incomplete',
                    'Please add your music Genre to complete your artist profile.'
                )

        # --- Step 2: Check for general incomplete profile fields ---
        general_fields = {
            'phone_number': 'Phone Number',
            'date_of_birth': 'Date of Birth',
            'address': 'Address',
            'gender': 'Gender'
        }
        
        for field_key, field_name in general_fields.items():
            if not getattr(user, field_key, None):
                add_dynamic_notification(
                    'Incomplete Profile',
                    f'Please add your {field_name} to complete your profile.'
                )

        # --- Step 3: Fetch persistent notifications from the database ---
        queryset = self.get_queryset()
        db_notifications = self.get_serializer(queryset, many=True).data

        # --- Step 4: Combine the lists and return the response ---
        all_notifications = dynamic_notifications + db_notifications
        
        return Response(all_notifications, status=status.HTTP_200_OK)