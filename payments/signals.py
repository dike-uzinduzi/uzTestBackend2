# payments/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment
from albums.models import PlaquePurchase

@receiver(post_save, sender=Payment)
def update_plaque_purchase_on_payment(sender, instance, **kwargs):
    if instance.status == "COMPLETED":  # Match your model's uppercase status
        try:
            purchase = PlaquePurchase.objects.get(transaction_id=instance.reference_number)
            purchase.payment_status = "COMPLETED"

            # Update plaque type dynamically
            plaque_type = purchase.get_plaque_type(purchase.contribution_amount)
            purchase.plaque.plaque_type = plaque_type
            purchase.plaque.save()

            purchase.save()
        except PlaquePurchase.DoesNotExist:
            pass
