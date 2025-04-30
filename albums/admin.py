from django.contrib import admin
from .models import Album, Track,Genre

class TrackInline(admin.TabularInline):
    model = Track
    extra = 1

class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'release_date', 'genre')
    inlines = [TrackInline]

    def has_add_permission(self, request, obj=None):
        # Only superusers can add albums
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        # Only superusers can edit albums
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete albums
        return request.user.is_superuser

admin.site.register(Album, AlbumAdmin)
admin.site.register(Genre)