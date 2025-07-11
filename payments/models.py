from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Updated payment method choices - only ZiG and USD methods
    PAYMENT_METHOD_CHOICES = [
        # USD Payment Methods
        ('PZW204', 'Visa'),
        ('PZW211', 'EcoCash USD'),
        # ZiG Payment Methods
        ('PZW201', 'EcoCash ZiG'),
        ('PZW210', 'PayGo ZiG'),
    ]

    # Currency choices - only USD and ZiG
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('ZiG', 'Zimbabwe Dollar'),
    ]

    # Plaque type choices based on amount ranges
    PLAQUE_TYPE_CHOICES = [
        ('thank_you', 'Thank You Message'),
        ('wood', 'Wood Plaque'),
        ('Gold', 'Gold Plaque'),
        ('Silver', 'Silver Plaque'),
        ('Emerald', 'Emerald Plaque'),
        ('gold', 'Premium Gold Plaque'),
        ('emerald', 'Premium Emerald Plaque'),
    ]

    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    reference_number = models.CharField(max_length=255, unique=True, db_index=True, null=True, blank=True)
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    payment_reason = models.CharField(max_length=255)
    
    # Customer details
    customer_email = models.EmailField()
    customerPhoneNumber = models.CharField(max_length=20, blank=True, null=True)
    customer_name = models.CharField(max_length=100, blank=True, null=True)
    
    # Payment status and tracking
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    poll_url = models.URLField(blank=True, null=True)
    redirect_url = models.URLField(blank=True, null=True)
    
    # Additional metadata
    payment_type = models.CharField(max_length=20, choices=[('SEAMLESS', 'Seamless'), ('REDIRECT', 'Redirect')])
    required_fields = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    # Support-specific fields
    album_title = models.CharField(max_length=255, blank=True, null=True)
    artist_name = models.CharField(max_length=255, blank=True, null=True)
    plaque_type = models.CharField(max_length=100, choices=PLAQUE_TYPE_CHOICES, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['reference_number']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['currency']),
            models.Index(fields=['payment_method']),
            models.Index(fields=['plaque_type']),
        ]

    def __str__(self):
        ref = self.reference_number or f"Payment-{str(self.id)[:8]}"
        return f"Payment {ref} - {self.amount} {self.currency} by {self.customer_email}"
    
    def get_payment_method_display_name(self):
        """Get user-friendly payment method name"""
        method_names = {
            'PZW204': 'Visa Card',
            'PZW211': 'EcoCash USD',
            'PZW201': 'EcoCash ZiG',
            'PZW210': 'PayGo ZiG',
        }
        return method_names.get(self.payment_method, self.payment_method)
    
    def get_currency_symbol(self):
        """Get currency symbol for display"""
        symbols = {
            'USD': '$',
            'ZiG': 'ZiG',
        }
        return symbols.get(self.currency, self.currency)
    
    def get_formatted_amount(self):
        """Get formatted amount with currency symbol"""
        symbol = self.get_currency_symbol()
        if self.currency == 'ZiG':
            return f"{symbol} {self.amount:.2f}"
        return f"{symbol}{self.amount:.2f}"
    
    def get_plaque_display_name(self):
        """Get user-friendly plaque type name"""
        plaque_names = {
            'thank_you': 'Thank You Message',
            'wood': 'Wood Plaque',
            'Gold': 'Gold Plaque',
            'Silver': 'Silver Plaque',
            'Emerald': 'Emerald Plaque',
            'gold': 'Premium Gold Plaque',
            'emerald': 'Premium Emerald Plaque',
        }
        return plaque_names.get(self.plaque_type, self.plaque_type)
    
    def get_plaque_type_by_amount(self):
        """Get the plaque type based on amount using ranges"""
        amount = float(self.amount)
        if amount < 51:
            return "thank_you"
        elif amount <= 100:
            return "wood"
        elif amount <= 300:
            return "Gold"
        elif amount <= 500:
            return "Silver"
        elif amount <= 700:
            return "Emerald"
        elif amount <= 900:
            return "gold"
        else:
            return "emerald"
    
    def validate_plaque_type(self):
        """Validate that plaque type matches the amount"""
        expected_plaque = self.get_plaque_type_by_amount()
        return self.plaque_type == expected_plaque
    
    def auto_assign_plaque_type(self):
        """Automatically assign plaque type based on amount"""
        self.plaque_type = self.get_plaque_type_by_amount()
        return self.plaque_type
    
    def get_estimated_delivery(self):
        """Get estimated delivery time based on plaque type"""
        delivery_times = {
            'thank_you': 'Digital delivery immediately',
            'wood': '1-2 weeks',
            'Gold': '2-3 weeks',
            'Silver': '3-4 weeks',
            'Emerald': '4-5 weeks',
            'gold': '3-4 weeks',
            'emerald': '5-6 weeks',
        }
        return delivery_times.get(self.plaque_type, '2-3 weeks')
    
    def mark_as_completed(self):
        """Mark payment as completed and set completion timestamp"""
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        
        # Auto-assign plaque type if not set or incorrect
        if not self.plaque_type or not self.validate_plaque_type():
            self.auto_assign_plaque_type()
        
        self.save(update_fields=['status', 'completed_at', 'plaque_type', 'updated_at'])
    
    def mark_as_failed(self):
        """Mark payment as failed"""
        self.status = 'FAILED'
        self.save(update_fields=['status', 'updated_at'])

    def save(self, *args, **kwargs):
        """Override save to auto-assign plaque type if not set"""
        if self.amount and not self.plaque_type:
            self.auto_assign_plaque_type()
        super().save(*args, **kwargs)

class PaymentLog(models.Model):
    """Log all payment-related events for debugging and audit trail"""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='logs')
    event_type = models.CharField(max_length=50)
    message = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        ref = self.payment.reference_number or f"Payment-{str(self.payment.id)[:8]}"
        return f"{ref} - {self.event_type} at {self.timestamp}"
