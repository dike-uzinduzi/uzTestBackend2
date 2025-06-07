from django.urls import path
from .views import CreatePaymentView, CheckPaymentStatusView,InitiatePaymentView

urlpatterns = [
    path('payments/create-payment/', CreatePaymentView.as_view(), name='create-payment'),
    path('payments/check-payment-status/<str:reference_number>/', CheckPaymentStatusView.as_view(), name='check-payment-status'),
    path('payments/initiate-payment/', InitiatePaymentView.as_view(), name='initiate_payment'),
     
]