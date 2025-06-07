from django.contrib import admin
from .models import Album, Track,Genre

class TrackInline(admin.TabularInline):
    model = Track
    extra = 1
class TrackAdmin(admin.ModelAdmin):
    list_display = ('title', 'album', 'duration', 'track_number', 'featured_artists')
    search_fields = ('title', 'album__title')

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'release_date', 'genre','duration', 'is_published', 'is_featured', 'created_at', 'updated_at')
    inlines = [TrackInline]

    def has_add_permission(self, request, obj=None):
       
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
       
        return request.user.is_superuser

admin.site.register(Album, AlbumAdmin)
admin.site.register(Genre)