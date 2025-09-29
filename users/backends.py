from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

class EmailOrUsernameBackend(ModelBackend):
    """
    This is a custom authentication backend that allows users to log in
    with either their username or email address.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        try:
            # Try to fetch the user by looking for a match in either the
            # username or email field. The Q object is used for OR queries.
            # `iexact` is used for case-insensitive matching.
            user = User.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between a non-existent and a valid user.
            User().set_password(password)
            return None

        # Check if the provided password is correct for the user.
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None