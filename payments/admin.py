from django.contrib import admin
from .models import Payment, PaymentLog

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'reference_number', 'user', 'amount', 'currency', 
        'payment_method', 'status', 'payment_type', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'payment_type', 'currency', 'created_at']
    search_fields = ['reference_number', 'customer_email', 'user__email', 'payment_reason']
    readonly_fields = ['id', 'reference_number', 'created_at', 'updated_at', 'completed_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'reference_number', 'status')
        }),
        ('Payment Details', {
            'fields': ('amount', 'currency', 'payment_method', 'payment_reason', 'payment_type')
        }),
        ('Customer Information', {
            'fields': ('customer_email', 'customerPhoneNumber', 'customer_name')
        }),
        ('Support Details', {
            'fields': ('album_title', 'artist_name', 'plaque_type'),
            'classes': ('collapse',)
        }),
        ('URLs', {
            'fields': ('poll_url', 'redirect_url'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = ['payment', 'event_type', 'message', 'timestamp']
    list_filter = ['event_type', 'timestamp']
    search_fields = ['payment__reference_number', 'message']
    readonly_fields = ['payment', 'event_type', 'message', 'data', 'timestamp']
    
    def has_add_permission(self, request):
        return False  # Prevent manual creation of logs
    
    def has_change_permission(self, request, obj=None):
        return False  # Make logs read-only
