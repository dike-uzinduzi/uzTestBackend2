from django.contrib import admin
from django.utils.html import format_html
from .models import *

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'reference_number', 'user', 'amount_currency', 'payment_method_display', 
        'status_display', 'payment_type', 'created_at', 'is_paid'
    ]
    list_filter = ['status', 'payment_method', 'payment_type', 'currency', 'created_at', 'completed_at']
    search_fields = ['reference_number', 'customer_email', 'user__email', 'payment_reason', 'customer_name']
    readonly_fields = ['id', 'reference_number', 'created_at', 'updated_at', 'completed_at', 'pesepay_transaction_id', 'pesepay_merchant_reference']
    actions = ['mark_as_success', 'mark_as_failed', 'mark_as_cancelled']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'reference_number', 'status')
        }),
        ('Payment Details', {
            'fields': ('amount', 'currency', 'payment_method', 'payment_reason', 'payment_type')
        }),
        ('PesePay Information', {
            'fields': ('pesepay_transaction_id', 'pesepay_merchant_reference', 'poll_url', 'redirect_url'),
            'classes': ('collapse',)
        }),
        ('Customer Information', {
            'fields': ('customer_email', 'customerPhoneNumber', 'customer_name')
        }),
        ('Support Details', {
            'fields': ('album_title', 'artist_name', 'plaque_type'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
        ('Additional Data', {
            'fields': ('required_fields',),
            'classes': ('collapse',)
        }),
    )
    
    def amount_currency(self, obj):
        return f"{obj.get_currency_symbol()}{obj.amount}"
    amount_currency.short_description = 'Amount'
    
    def payment_method_display(self, obj):
        return obj.get_payment_method_display_name()
    payment_method_display.short_description = 'Payment Method'
    
    def status_display(self, obj):
        status_color_map = {
            'SUCCESS': 'green',
            'FAILED': 'red',
            'CANCELLED': 'orange',
            'PENDING': 'blue',
            'PROCESSING': 'purple',
            'INITIATED': 'gray',
            'AUTHORIZATION_FAILED': 'darkred',
            'DECLINED': 'darkred',
            'INSUFFICIENT_FUNDS': 'darkred',
            'SERVICE_UNAVAILABLE': 'darkorange',
            'TIME_OUT': 'darkorange',
            'COLLECTED': 'green',
            'DELIVERED': 'green',
        }
        color = status_color_map.get(obj.status, 'black')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.get_status_display())
    status_display.short_description = 'Status'
    
    def is_paid(self, obj):
        paid_statuses = ['SUCCESS', 'COLLECTED', 'DELIVERED']
        return obj.status in paid_statuses
    is_paid.boolean = True
    is_paid.short_description = 'Paid'
    
    def mark_as_success(self, request, queryset):
        updated = queryset.update(status='SUCCESS')
        self.message_user(request, f"{updated} payments marked as SUCCESS.")
    mark_as_success.short_description = "Mark selected payments as SUCCESS"
    
    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status='FAILED')
        self.message_user(request, f"{updated} payments marked as FAILED.")
    mark_as_failed.short_description = "Mark selected payments as FAILED"
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='CANCELLED')
        self.message_user(request, f"{updated} payments marked as CANCELLED.")
    mark_as_cancelled.short_description = "Mark selected payments as CANCELLED"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of payments to maintain audit trail
        return False

@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = ['payment_reference', 'event_type', 'timestamp', 'short_message']
    list_filter = ['event_type', 'timestamp']
    search_fields = ['payment__reference_number', 'message', 'event_type']
    readonly_fields = ['payment', 'event_type', 'message', 'data', 'timestamp']
    date_hierarchy = 'timestamp'
    
    def payment_reference(self, obj):
        return obj.payment.reference_number or f"Payment-{str(obj.payment.id)[:8]}"
    payment_reference.short_description = 'Payment Reference'
    
    def short_message(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    short_message.short_description = 'Message'
    
    def has_add_permission(self, request):
        return False  # Prevent manual creation of logs
    
    def has_change_permission(self, request, obj=None):
        return False  # Make logs read-only
    
    def has_delete_permission(self, request, obj=None):
        return False  # Prevent deletion of logs to maintain audit trail
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('payment')
    
    
@admin.register(ToBeVerifiedPayment)
class ToBeVerifiedPaymentAdmin(admin.ModelAdmin):
    list_display = ('payment', 'reason', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('payment__reference_number', 'reason')