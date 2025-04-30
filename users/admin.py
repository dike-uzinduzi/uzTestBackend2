from django.contrib import admin
from .models import UserAccount #Artist, Fan, Album, Track, Plaque,Profile

# Register your models here.
admin.site.register(UserAccount)
"""
admin.site.register(Fan)
admin.site.register(Album)
admin.site.register(Track)
admin.site.register(Plaque)
admin.site.register(Profile)
"""