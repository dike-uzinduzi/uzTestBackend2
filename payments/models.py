from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid
import json
import logging

logger = logging.getLogger(__name__)

class Payment(models.Model):
    # PesePay payment method choices
    PAYMENT_METHOD_CHOICES = [
        # USD Payment Methods
        ('PZW204', 'Visa'),
        ('PZW211', 'EcoCash USD'),
        # ZiG Payment Methods
        ('PZW201', 'EcoCash ZiG'),
        ('PZW210', 'PayGo ZiG'),
        # Cash Payment Method (not part of PesePay)
        ('CASH001', 'Cash Collection'),
    ]

    # Exact PesePay transaction statuses
    PAYMENT_STATUS_CHOICES = [
        ('AUTHORIZATION_FAILED', 'Authorization Failed'),
        ('CANCELLED', 'Cancelled'),
        ('CLOSED', 'Closed'),
        ('CLOSED_PERIOD_ELAPSED', 'Closed - Period Elapsed'),
        ('DECLINED', 'Declined'),
        ('ERROR', 'Error'),
        ('FAILED', 'Failed'),
        ('INITIATED', 'Initiated'),
        ('INSUFFICIENT_FUNDS', 'Insufficient Funds'),
        ('PARTIALLY_PAID', 'Partially Paid'),
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('REVERSED', 'Reversed'),
        ('SERVICE_UNAVAILABLE', 'Service Unavailable'),
        ('SUCCESS', 'Success'),
        ('TERMINATED', 'Terminated'),
        ('TIME_OUT', 'Time Out'),
        # Additional statuses for cash payments (not part of PesePay)
        ('COLLECTED', 'Cash Collected'),
        ('DELIVERED', 'Delivered'),
    ]

    # Currency choices
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
    status = models.CharField(max_length=25, choices=PAYMENT_STATUS_CHOICES, default='INITIATED')
    poll_url = models.URLField(blank=True, null=True)
    redirect_url = models.URLField(blank=True, null=True)
    
    # PesePay-specific fields
    pesepay_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    pesepay_merchant_reference = models.CharField(max_length=255, blank=True, null=True)
    
    # Additional metadata
    payment_type = models.CharField(max_length=20, choices=[('SEAMLESS', 'Seamless'), ('REDIRECT', 'Redirect'), ('CASH', 'Cash')])
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
            models.Index(fields=['pesepay_transaction_id']),
            models.Index(fields=['pesepay_merchant_reference']),
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
            'CASH001': 'Cash Collection',
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
    
    def mark_as_success(self):
        """Mark payment as successful (PesePay SUCCESS status)"""
        self.status = 'SUCCESS'
        self.completed_at = timezone.now()
        
        # Auto-assign plaque type if not set or incorrect
        if not self.plaque_type or not self.validate_plaque_type():
            self.auto_assign_plaque_type()
        
        self.save(update_fields=['status', 'completed_at', 'plaque_type', 'updated_at'])
    
    def mark_as_failed(self):
        """Mark payment as failed (PesePay FAILED status)"""
        self.status = 'FAILED'
        self.save(update_fields=['status', 'updated_at'])
    
    def mark_as_cancelled(self):
        """Mark payment as cancelled (PesePay CANCELLED status)"""
        self.status = 'CANCELLED'
        self.save(update_fields=['status', 'updated_at'])
    
    def mark_as_pending(self):
        """Mark payment as pending (PesePay PENDING status)"""
        self.status = 'PENDING'
        self.save(update_fields=['status', 'updated_at'])
    
    def is_pesepay_payment(self):
        """Check if this is a PesePay payment (not cash)"""
        return self.payment_method != 'CASH001'
    
    def update_from_pesepay_response(self, pesepay_response):
        """
          Update payment record based on Pesepay API response.
          Accepts either:
              - A Pesepay object with attributes (referenceNumber, status, paid)
              - OR a decrypted payload dict from check-payment API
        """
        if isinstance(pesepay_response, dict):
            payload = pesepay_response
            pesepay_status = payload.get('status', '').upper().strip()
            reference_number = payload.get('referenceNumber', self.reference_number)
            transaction_id = payload.get('transactionId', self.pesepay_transaction_id)
            merchant_reference = payload.get('merchantReference', self.pesepay_merchant_reference)
            paid = payload.get('paid', False)
        else:
            # Wrapper object
            payload = None
            pesepay_status = str(getattr(pesepay_response, 'status', '')).upper().strip()
            reference_number = getattr(pesepay_response, 'referenceNumber', self.reference_number)
            transaction_id = getattr(pesepay_response, 'transactionId', self.pesepay_transaction_id)
            merchant_reference = getattr(pesepay_response, 'merchantReference', self.pesepay_merchant_reference)
            paid = getattr(pesepay_response, 'paid', False)

        old_status = self.status
        valid_statuses = [choice[0] for choice in self.PAYMENT_STATUS_CHOICES]

    # Update IDs & URLs
        self.reference_number = reference_number
        self.pesepay_transaction_id = transaction_id
        self.pesepay_merchant_reference = merchant_reference
        self.poll_url = getattr(pesepay_response, 'pollUrl', self.poll_url)
        self.redirect_url = getattr(pesepay_response, 'redirectUrl', self.redirect_url)

    # Normalize status
        if pesepay_status in valid_statuses:
            self.status = pesepay_status
        else:
          self.status = 'ERROR'
          PaymentLog.objects.create(
            payment=self,
            event_type='UNKNOWN_STATUS',
            message=f"Received unknown status from PesePay: {pesepay_status}",
            data={'pesepay_response': str(pesepay_response)}
        )

    # Handle success/failure timestamps
        if self.status == 'SUCCESS':
            self.completed_at = timezone.now()
        elif self.status in [
           'FAILED', 'CANCELLED', 'TIME_OUT', 'DECLINED', 'AUTHORIZATION_FAILED',
           'CLOSED', 'CLOSED_PERIOD_ELAPSED', 'INSUFFICIENT_FUNDS',
           'ERROR', 'TERMINATED'
      ]:
          self.completed_at = None

    # Auto-assign plaque if needed
        if not self.plaque_type or not self.validate_plaque_type():
           self.auto_assign_plaque_type()

        self.save()

    # Log status change
        if old_status != self.status:
             PaymentLog.objects.create(
               payment=self,
                event_type='STATUS_UPDATE',
                message=f"Status changed from {old_status} → {self.status}",
               data={'pesepay_response': str(pesepay_response)}
        )

        print(f"✅ Payment {self.id} updated to status {self.status}")

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
    
class ToBeVerifiedPayment(models.Model):
    payment = models.OneToOneField(
        'Payment',
        on_delete=models.CASCADE,
        related_name='to_be_verified'
    )
    reason = models.CharField(max_length=255, default='Payment timeout')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"ToBeVerifiedPayment: {self.payment.reference_number}"