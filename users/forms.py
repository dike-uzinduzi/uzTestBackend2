from django import forms
from .models import UserAccount

class UserAccountUpdateForm(forms.ModelForm):
    class Meta:
        model = UserAccount
        fields = [
            'first_name', 'last_name', 'address', 'phone_number', 'whatsapp_number',
            'date_of_birth', 'national_id_number', 'citizenship', 'country_of_residence',
            'profile_pic', 'cover_photo'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
