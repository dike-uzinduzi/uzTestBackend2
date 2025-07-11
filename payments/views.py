from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from pesepay import Pesepay
import json
from django.http import JsonResponse
import logging
from .models import Payment, PaymentLog
from .serializers import PaymentSerializer
from django.db import transaction
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

# Initialize Pesepay
pesepay = Pesepay( settings.PESEPAY_ENCRYPTION_KEY,settings.PESEPAY_INTEGRATION_KEY,)
pesepay.result_url = settings.PESEPAY_RESULT_URL
pesepay.return_url = settings.PESEPAY_RETURN_URL

class CreateSeamlessPaymentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create and process a seamless payment"""
        data = request.data
        user = request.user
        
        try:
            with transaction.atomic():
                # Create payment record first WITHOUT reference_number
                payment_record = Payment.objects.create(
                    user=user,
                    amount=data.get('amount'),
                    currency=data.get('currency_code', 'USD'),
                    payment_method=data.get('payment_method_code'),
                    payment_reason=data.get('payment_reason'),
                    customer_email=data.get('email', user.email),
                    customerPhoneNumber=data.get('phone_number', ''),
                    customer_name=data.get('customer_name', f"{user.first_name} {user.last_name}".strip()),
                    payment_type='SEAMLESS',
                    required_fields=data.get('required_fields', {}),
                    # Support-specific fields
                    album_title=data.get('album_title'),
                    artist_name=data.get('artist_name'),
                    plaque_type=data.get('plaque_type'),
                    # Don't set reference_number yet - it will come from Pesepay
                )
                
                # Log payment creation
                PaymentLog.objects.create(
                    payment=payment_record,
                    event_type='CREATED',
                    message='Seamless payment record created',
                    data=data
                )
                
                logger.info(f"Created payment record with ID: {payment_record.id}")
                logger.info(f"Creating Pesepay payment with parameters:")
                logger.info(f"  currency: {payment_record.currency}")
                logger.info(f"  payment_method: {payment_record.payment_method}")
                logger.info(f"  email: {payment_record.customer_email}")
                logger.info(f"  phone: {payment_record.customerPhoneNumber}")
                logger.info(f"  name: {payment_record.customer_name}")

                try:
                    # Create Pesepay payment using positional arguments
                    payment = pesepay.create_payment(
                        payment_record.currency,
                        payment_record.payment_method,
                        payment_record.customer_email,
                        payment_record.customerPhoneNumber,
                        payment_record.customer_name
                    )
                    logger.info(f"Pesepay payment created successfully")
                except Exception as e:
                    logger.error(f"Failed to create Pesepay payment: {str(e)}")
                    # Mark payment as failed and log the error
                    payment_record.mark_as_failed()
                    PaymentLog.objects.create(
                        payment=payment_record,
                        event_type='PESEPAY_CREATE_FAILED',
                        message=f'Failed to create Pesepay payment: {str(e)}',
                        data={'error': str(e), 'error_type': type(e).__name__}
                    )
                    raise
                
                # Process required fields
                required_fields = data.get('required_fields', {})
                if not required_fields:
                    required_fields = {'default': 'value'}
                
                try:
                    # Make seamless payment
                    response = pesepay.make_seamless_payment(
                        payment, 
                        payment_record.payment_reason, 
                        float(payment_record.amount), 
                        required_fields
                    )
                    logger.info(f"Pesepay seamless payment response: success={response.success}")
                except Exception as e:
                    logger.error(f"Failed to make seamless payment: {str(e)}")
                    payment_record.mark_as_failed()
                    PaymentLog.objects.create(
                        payment=payment_record,
                        event_type='PESEPAY_SEAMLESS_FAILED',
                        message=f'Failed to make seamless payment: {str(e)}',
                        data={'error': str(e), 'error_type': type(e).__name__}
                    )
                    raise
                
                if response.success:
                    # Update payment record with Pesepay response
                    payment_record.reference_number = response.referenceNumber
                    payment_record.poll_url = response.pollUrl
                    if hasattr(response, 'redirectUrl'):
                        payment_record.redirect_url = response.redirectUrl
                    
                    # Save the updated payment record
                    try:
                        payment_record.save(update_fields=['reference_number', 'poll_url', 'redirect_url', 'updated_at'])
                        logger.info(f"Updated payment record with reference: {response.referenceNumber}")
                    except Exception as e:
                        logger.error(f"Failed to save payment record: {str(e)}")
                        # If we can't save the reference number, still try to continue
                        # but log the issue
                        PaymentLog.objects.create(
                            payment=payment_record,
                            event_type='SAVE_ERROR',
                            message=f'Failed to save reference number: {str(e)}',
                            data={'reference_number': response.referenceNumber, 'error': str(e)}
                        )
                    
                    # Log successful creation
                    PaymentLog.objects.create(
                        payment=payment_record,
                        event_type='PESEPAY_SUCCESS',
                        message='Pesepay seamless payment initiated successfully',
                        data={
                            'reference_number': response.referenceNumber,
                            'poll_url': response.pollUrl
                        }
                    )
                    
                    return Response({
                        'success': True,
                        'payment_id': str(payment_record.id),
                        'reference_number': response.referenceNumber,
                        'poll_url': response.pollUrl,
                        'redirect_url': getattr(response, 'redirectUrl', None),
                        'message': 'Payment initiated successfully'
                    }, status=status.HTTP_201_CREATED)
                else:
                    # Mark payment as failed
                    payment_record.mark_as_failed()
                    
                    # Log failure
                    PaymentLog.objects.create(
                        payment=payment_record,
                        event_type='PESEPAY_FAILED',
                        message=f'Pesepay seamless payment failed: {response.message}',
                        data={'error_message': response.message}
                    )
                    
                    return Response({
                        'success': False,
                        'message': response.message,
                        'payment_id': str(payment_record.id)
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
        except Exception as e:
            logger.exception("Error in CreateSeamlessPaymentView")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InitiateRedirectPaymentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create and initiate a redirect payment"""
        data = request.data
        user = request.user
        
        try:
            with transaction.atomic():
                # Create payment record WITHOUT reference_number
                payment_record = Payment.objects.create(
                    user=user,
                    amount=data.get('amount'),
                    currency=data.get('currency_code', 'USD'),
                    payment_method=data.get('payment_method_code', 'REDIRECT'),
                    payment_reason=data.get('payment_reason'),
                    customer_email=data.get('email', user.email),
                    customerPhoneNumber=data.get('customerPhoneNumber', ''),
                    customer_name=data.get('customer_name', f"{user.first_name} {user.last_name}".strip()),
                    payment_type='REDIRECT',
                    # Support-specific fields
                    album_title=data.get('album_title'),
                    artist_name=data.get('artist_name'),
                    plaque_type=data.get('plaque_type'),
                    # Don't set reference_number yet
                )
                
                # Log payment creation
                PaymentLog.objects.create(
                    payment=payment_record,
                    event_type='CREATED',
                    message='Redirect payment record created',
                    data=data
                )
                
                logger.info(f"Created payment record with ID: {payment_record.id}")
                logger.info(f"Creating Pesepay transaction with parameters:")
                logger.info(f"  amount: {payment_record.amount}")
                logger.info(f"  currency: {payment_record.currency}")
                logger.info(f"  reason: {payment_record.payment_reason}")

                try:
                    transaction_obj = pesepay.create_transaction(
                        float(payment_record.amount),
                        payment_record.currency,
                        payment_record.payment_reason
                    )
                    logger.info(f"Pesepay transaction created successfully")
                except Exception as e:
                    logger.error(f"Failed to create Pesepay transaction: {str(e)}")
                    payment_record.mark_as_failed()
                    PaymentLog.objects.create(
                        payment=payment_record,
                        event_type='PESEPAY_CREATE_FAILED',
                        message=f'Failed to create Pesepay transaction: {str(e)}',
                        data={'error': str(e), 'error_type': type(e).__name__}
                    )
                    raise
                
                try:
                    # Initiate transaction
                    response = pesepay.initiate_transaction(transaction_obj)
                    logger.info(f"Pesepay transaction initiation response: success={response.success}")
                except Exception as e:
                    logger.error(f"Failed to initiate transaction: {str(e)}")
                    payment_record.mark_as_failed()
                    PaymentLog.objects.create(
                        payment=payment_record,
                        event_type='PESEPAY_INITIATE_FAILED',
                        message=f'Failed to initiate transaction: {str(e)}',
                        data={'error': str(e), 'error_type': type(e).__name__}
                    )
                    raise
                
                if response.success:
                    # Update payment record
                    payment_record.reference_number = response.referenceNumber
                    payment_record.poll_url = getattr(response, 'pollUrl', None)
                    payment_record.redirect_url = response.redirectUrl
                    
                    try:
                        payment_record.save(update_fields=['reference_number', 'poll_url', 'redirect_url', 'updated_at'])
                        logger.info(f"Updated payment record with reference: {response.referenceNumber}")
                    except Exception as e:
                        logger.error(f"Failed to save payment record: {str(e)}")
                        PaymentLog.objects.create(
                            payment=payment_record,
                            event_type='SAVE_ERROR',
                            message=f'Failed to save reference number: {str(e)}',
                            data={'reference_number': response.referenceNumber, 'error': str(e)}
                        )
                    
                    # Log successful initiation
                    PaymentLog.objects.create(
                        payment=payment_record,
                        event_type='PESEPAY_SUCCESS',
                        message='Pesepay redirect payment initiated successfully',
                        data={
                            'reference_number': response.referenceNumber,
                            'redirect_url': response.redirectUrl
                        }
                    )
                    
                    return Response({
                        'success': True,
                        'payment_id': str(payment_record.id),
                        'reference_number': response.referenceNumber,
                        'redirect_url': response.redirectUrl,
                        'poll_url': getattr(response, 'pollUrl', None),
                        'message': 'Payment initiated successfully'
                    }, status=status.HTTP_201_CREATED)
                else:
                    # Mark payment as failed
                    payment_record.mark_as_failed()
                    
                    # Log failure
                    PaymentLog.objects.create(
                        payment=payment_record,
                        event_type='PESEPAY_FAILED',
                        message=f'Pesepay redirect payment failed: {response.message}',
                        data={'error_message': response.message}
                    )
                    
                    return Response({
                        'success': False,
                        'message': response.message,
                        'payment_id': str(payment_record.id)
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
        except Exception as e:
            logger.exception("Error in InitiateRedirectPaymentView")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CheckPaymentStatusView(APIView):
    permission_classes = [AllowAny]  # Allow checking status without authentication
    
    def get(self, request, reference_number):
        """Check payment status using reference number"""
        try:
            # Get payment record from database
            payment_record = get_object_or_404(Payment, reference_number=reference_number)
            
            # Check with Pesepay
            response = pesepay.check_payment(reference_number)
            
            # Log status check
            PaymentLog.objects.create(
                payment=payment_record,
                event_type='STATUS_CHECK',
                message='Payment status checked',
                data={
                    'pesepay_success': response.success,
                    'pesepay_paid': getattr(response, 'paid', False),
                    'pesepay_message': getattr(response, 'message', '')
                }
            )
            
            if response.success:
                # Update payment status if it changed
                if response.paid and payment_record.status != 'COMPLETED':
                    payment_record.mark_as_completed()
                    
                    # Log completion
                    PaymentLog.objects.create(
                        payment=payment_record,
                        event_type='COMPLETED',
                        message='Payment marked as completed',
                        data={'completed_at': payment_record.completed_at.isoformat()}
                    )
                
                return Response({
                    'success': True,
                    'paid': response.paid,
                    'status': 'Paid' if response.paid else 'Unpaid',
                    'payment_details': {
                        'id': str(payment_record.id),
                        'amount': str(payment_record.amount),
                        'currency': payment_record.currency,
                        'payment_reason': payment_record.payment_reason,
                        'customer_email': payment_record.customer_email,
                        'created_at': payment_record.created_at.isoformat(),
                        'album_title': payment_record.album_title,
                        'artist_name': payment_record.artist_name,
                        'plaque_type': payment_record.plaque_type,
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': response.message
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Payment.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Payment not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("Error in CheckPaymentStatusView")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PaymentReturnView(APIView):
    """Handle return from Pesepay payment page"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Handle GET request from Pesepay return URL"""
        reference_number = request.GET.get('referenceNumber')
        transaction_status = request.GET.get('transactionStatus')
        
        try:
            if reference_number:
                payment_record = get_object_or_404(Payment, reference_number=reference_number)
                
                # Log return
                PaymentLog.objects.create(
                    payment=payment_record,
                    event_type='RETURN',
                    message=f'Payment return received with status: {transaction_status}',
                    data={
                        'transaction_status': transaction_status,
                        'query_params': dict(request.GET)
                    }
                )
                
                # Update status based on transaction status
                if transaction_status == 'COMPLETED':
                    payment_record.mark_as_completed()
                elif transaction_status == 'FAILED':
                    payment_record.mark_as_failed()
                
                return Response({
                    'success': True,
                    'reference_number': reference_number,
                    'transaction_status': transaction_status,
                    'payment_details': PaymentSerializer(payment_record).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Missing reference number'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Payment.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Payment not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("Error in PaymentReturnView")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PaymentResultView(APIView):
    """Handle result callback from Pesepay"""
    permission_classes = [AllowAny]
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        """Handle POST request from Pesepay result URL"""
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body)
            reference_number = data.get('referenceNumber')
            
            if reference_number:
                payment_record = get_object_or_404(Payment, reference_number=reference_number)
                
                # Log result
                PaymentLog.objects.create(
                    payment=payment_record,
                    event_type='RESULT',
                    message='Payment result received from Pesepay',
                    data=data
                )
                
                # Process result based on status
                transaction_status = data.get('transactionStatus')
                if transaction_status == 'COMPLETED':
                    payment_record.mark_as_completed()
                elif transaction_status in ['FAILED', 'CANCELLED']:
                    payment_record.mark_as_failed()
                
                return Response({
                    'success': True,
                    'message': 'Result processed successfully'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Missing reference number'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.exception("Error in PaymentResultView")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserPaymentsView(APIView):
    """Get user's payment history"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get current user's payments"""
        payments = Payment.objects.filter(user=request.user)
        serializer = PaymentSerializer(payments, many=True)
        return Response({
            'success': True,
            'payments': serializer.data
        }, status=status.HTTP_200_OK)

class PaymentDetailView(APIView):
    """Get detailed payment information"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, payment_id):
        """Get payment details by ID"""
        try:
            payment = get_object_or_404(Payment, id=payment_id, user=request.user)
            serializer = PaymentSerializer(payment)
            
            return Response({
                'success': True,
                'payment': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Payment.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Payment not found'
            }, status=status.HTTP_404_NOT_FOUND)
