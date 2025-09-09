from django.urls import path
from .views import *

urlpatterns = [
    # Payment creation
    path('payments/seamless/', CreateSeamlessPaymentView.as_view(), name='create-seamless-payment'),
    path('payments/redirect/', InitiateRedirectPaymentView.as_view(), name='initiate-redirect-payment'),
    
    # Payment status and details I am using these
    path('payments/status/<str:reference_number>/', CheckPaymentStatusView.as_view(), name='check-payment-status'),
    path('payments/user/', UserPaymentsView.as_view(), name='user-payments'),
    path('payments/detail/<uuid:payment_id>/', PaymentDetailView.as_view(), name='payment-detail'),
     path('to-be-verified/', MarkPaymentToBeVerifiedView.as_view(), name='to_be_verified_payment'),
    
    # Pesepay callbacks
    path('payments/return/', PaymentReturnView.as_view(), name='payment-return'),
    path('payments/result/', PaymentResultView.as_view(), name='payment-result'),
    path('dashboard/payments/', UserDashboardAPIView.as_view(), name='user-dashboard-payments'),
    
    # Legacy endpoints (for backward compatibility)
    path('payments/create-payment/', CreateSeamlessPaymentView.as_view(), name='create-payment-legacy'),
    path('payments/initiate-payment/', InitiateRedirectPaymentView.as_view(), name='initiate-payment-legacy'),
    path('payments/check-payment-status/<str:reference_number>/', CheckPaymentStatusView.as_view(), name='check-payment-status-legacy'),
      # Cash payment endpoints
    path('payments/cash/', CreateCashPaymentView.as_view(), name='create-cash-payment'),
    path('payments/cash/<uuid:payment_id>/status/', UpdateCashPaymentStatusView.as_view(), name='update-cash-payment-status'),
    path('payments/cash/<uuid:payment_id>/', CashPaymentDetailView.as_view(), name='cash-payment-detail'),
]
