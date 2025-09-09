from django.contrib import admin
from .models import Album, Track, Genre, AlbumActivity, Plaque, PlaquePurchase

# ---------------------------
# Inline Track Management
# ---------------------------
class TrackInline(admin.TabularInline):
    model = Track
    extra = 1
    fields = ('track_number', 'title', 'duration', 'featured_artists')
    readonly_fields = ('duration',)


# ---------------------------
# Track Admin
# ---------------------------
class TrackAdmin(admin.ModelAdmin):
    list_display = ('title', 'album', 'duration', 'track_number', 'featured_artists', 'is_published')
    list_filter = ('is_published', 'album')
    search_fields = ('title', 'album__title', 'featured_artists')

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# ---------------------------
# Album Admin
# ---------------------------
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'release_date', 'genre', 'duration', 'is_published', 'is_featured', 'created_at', 'updated_at')
    list_filter = ('is_published', 'is_featured', 'genre')
    search_fields = ('title', 'artist__username')
    inlines = [TrackInline]

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# ---------------------------
# Plaque Admin
# ---------------------------
class PlaqueAdmin(admin.ModelAdmin):
    list_display = ('plaque_type', 'hash_key')
    search_fields = ('plaque_type', 'hash_key')


# ---------------------------
# Plaque Purchase Admin
# ---------------------------
class PlaquePurchaseAdmin(admin.ModelAdmin):
    list_display = ('plaque', 'fan', 'album_supported', 'contribution_amount', 'payment_status', 'purchase_date')
    list_filter = ('payment_status', 'purchase_date')
    search_fields = ('fan__username', 'album_supported__title', 'transaction_id', 'hash_key')


# ---------------------------
# Register Models
# ---------------------------
admin.site.register(Album, AlbumAdmin)
admin.site.register(Track, TrackAdmin)
admin.site.register(Genre)
admin.site.register(AlbumActivity)
admin.site.register(Plaque, PlaqueAdmin)
admin.site.register(PlaquePurchase, PlaquePurchaseAdmin)
