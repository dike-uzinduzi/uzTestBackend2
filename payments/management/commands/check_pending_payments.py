from django.core.management.base import BaseCommand
from django.conf import settings
from pesepay import Pesepay
from payments.models import Payment, PaymentLog
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Check status of pending payments and update database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Check payments from the last N hours (default: 24)'
        )
    
    def handle(self, *args, **options):
        hours = options['hours']
        
        # Initialize Pesepay
        pesepay = Pesepay(settings.PESEPAY_INTEGRATION_KEY, settings.PESEPAY_ENCRYPTION_KEY)
        
        # Get pending payments from the last N hours
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_time = timezone.now() - timedelta(hours=hours)
        pending_payments = Payment.objects.filter(
            status='PENDING',
            created_at__gte=cutoff_time
        )
        
        self.stdout.write(f"Checking {pending_payments.count()} pending payments...")
        
        updated_count = 0
        for payment in pending_payments:
            try:
                response = pesepay.check_payment(payment.reference_number)
                
                if response.success and response.paid:
                    payment.mark_as_completed()
                    updated_count += 1
                    
                    PaymentLog.objects.create(
                        payment=payment,
                        event_type='AUTO_COMPLETED',
                        message='Payment automatically marked as completed by management command',
                        data={'checked_at': timezone.now().isoformat()}
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ Payment {payment.reference_number} marked as completed")
                    )
                
            except Exception as e:
                logger.exception(f"Error checking payment {payment.reference_number}")
                self.stdout.write(
                    self.style.ERROR(f"✗ Error checking payment {payment.reference_number}: {str(e)}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"Completed! Updated {updated_count} payments.")
        )
