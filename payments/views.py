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
from django.utils import timezone
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
            
            # Define final statuses that don't need further checking
            FINAL_STATUSES = [
                'AUTHORIZATION_FAILED', 'CANCELLED', 'CLOSED', 'CLOSED_PERIOD_ELAPSED',
                'DECLINED', 'ERROR', 'FAILED', 'INSUFFICIENT_FUNDS', 'REVERSED',
                'SERVICE_UNAVAILABLE', 'SUCCESS', 'TERMINATED', 'TIME_OUT',
                'COLLECTED', 'DELIVERED'
            ]
            
            # For cash payments or payments with final status, return stored status
            if not payment_record.is_pesepay_payment() or payment_record.status in FINAL_STATUSES:
                # Determine if payment is paid based on status
                is_paid = payment_record.status == 'SUCCESS'
                
                return Response({
                    'success': True,
                    'paid': is_paid,
                    'status': payment_record.status,
                    'is_final_status': payment_record.status in FINAL_STATUSES,
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
            
            # For PesePay payments with non-final status, check with PesePay
            response = pesepay.check_payment(reference_number)
            
            # Log status check
            PaymentLog.objects.create(
                payment=payment_record,
                event_type='STATUS_CHECK',
                message='Payment status checked with PesePay',
                data={
                    'pesepay_success': response.success,
                    'pesepay_status': getattr(response, 'status', 'UNKNOWN'),
                    'pesepay_paid': getattr(response, 'paid', False),
                    'pesepay_message': getattr(response, 'message', '')
                }
            )
            
            if response.success:
                # Update payment record with PesePay response
                payment_record.update_from_pesepay_response(response)
                
                # If payment is successful, mark as completed
                if getattr(response, 'paid', False) and payment_record.status == 'SUCCESS':
                    payment_record.mark_as_success()
                    
                    # Log completion
                    PaymentLog.objects.create(
                        payment=payment_record,
                        event_type='COMPLETED',
                        message='Payment marked as completed',
                        data={'completed_at': payment_record.completed_at.isoformat()}
                    )
                
                # Determine if payment is paid based on status
                is_paid = payment_record.status == 'SUCCESS'
                
                return Response({
                    'success': True,
                    'paid': is_paid,
                    'status': payment_record.status,
                    'is_final_status': payment_record.status in FINAL_STATUSES,
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
                # Even if the PesePay API call failed, return the current status
                return Response({
                    'success': False,
                    'message': response.message,
                    'paid': False,
                    'status': payment_record.status,
                    'is_final_status': payment_record.status in FINAL_STATUSES,
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

class CreateCashPaymentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create a cash payment record"""
        data = request.data
        user = request.user
        
        try:
            with transaction.atomic():
                # Validate required fields for cash payments
                required_fields = ['amount', 'currency', 'customer_email', 'customer_name', 'customer_address']
                for field in required_fields:
                    if field not in data or not data[field]:
                        return Response({
                            'success': False,
                            'message': f'Missing required field: {field}'
                        }, status=status.HTTP_400_BAD_REQUEST)
                
                # Create payment record
                payment_record = Payment.objects.create(
                     # No reference number for cash payments
                    user=user,
                    reference_number=f"CASH-{payment_record.id}",
                    amount=data.get('amount'),
                    currency=data.get('currency_code'),
                    payment_method='CASH001',  # Special code for cash payments
                    payment_reason=data.get('payment_reason', 'Album Support'),
                    customer_email=data.get('email', user.email),
                    customerPhoneNumber=data.get('customer_phone', ''),
                    customer_name=data.get('customer_name', ''),
                    payment_type='CASH',
                    status='PENDING',  # Cash payments start as pending until collected
                    required_fields={
                        'address': data.get('customer_address', ''),
                        'phone': data.get('customer_phone', ''),
                        'agreed_terms': data.get('agree_terms', False),
                        'terms_accepted_at': timezone.now().isoformat()
                    },
                    # Support-specific fields
                    album_title=data.get('album_title'),
                    artist_name=data.get('artist_name'),
                    plaque_type=data.get('plaque_type'),
                )
                
                # Log payment creation
                PaymentLog.objects.create(
                    payment=payment_record,
                    event_type='CASH_PAYMENT_CREATED',
                    message='Cash payment record created',
                    data={
                        'customer_name': data.get('customer_name'),
                        'customer_address': data.get('customer_address'),
                        'customer_phone': data.get('customer_phone'),
                        'amount': data.get('amount'),
                        'currency': data.get('currency')
                    }
                )
                
                # In a real implementation, you might:
                # 1. Send a confirmation email to the customer
                # 2. Send a notification to admin about the cash payment
                # 3. Schedule delivery or pickup
                
                # For now, we'll simulate these actions with logs
                logger.info(f"Cash payment created: {payment_record.id}")
                logger.info(f"Customer: {data.get('customer_name')}")
                logger.info(f"Address: {data.get('customer_address')}")
                logger.info(f"Amount: {data.get('amount')} {data.get('currency')}")
                
                return Response({
                    'success': True,
                    'payment_id': str(payment_record.id),
                    'reference_number': payment_record.reference_number,
                    'message': 'Cash payment recorded successfully. We will contact you to arrange delivery and payment collection.',
                    'payment_details': {
                        'amount': str(payment_record.amount),
                        'currency': payment_record.currency,
                        'customer_name': payment_record.customer_name,
                        'customer_email': payment_record.customer_email,
                        'customer_phone': payment_record.customerPhoneNumber,
                        'customer_address': payment_record.required_fields.get('address', ''),
                        'estimated_delivery': payment_record.get_estimated_delivery()
                    }
                }, status=status.HTTP_201_CREATED)
                  
        except Exception as e:
            logger.exception("Error in CreateCashPaymentView")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateCashPaymentStatusView(APIView):
    """Update the status of a cash payment (for admin use)"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, payment_id):
        """Update cash payment status (e.g., mark as collected, delivered, etc.)"""
        try:
            payment = get_object_or_404(Payment, id=payment_id, payment_method='CASH001')
            
            # Only allow admins or the payment owner to update status
            if not (request.user.is_staff or payment.user == request.user):
                return Response({
                    'success': False,
                    'message': 'Permission denied'
                }, status=status.HTTP_403_FORBIDDEN)
            
            new_status = request.data.get('status')
            notes = request.data.get('notes', '')
            
            if new_status not in ['PENDING', 'COLLECTED', 'DELIVERED', 'COMPLETED', 'FAILED']:
                return Response({
                    'success': False,
                    'message': 'Invalid status'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update payment status
            old_status = payment.status
            payment.status = new_status
            
            # Add status change to required_fields
            status_history = payment.required_fields.get('status_history', [])
            status_history.append({
                'old_status': old_status,
                'new_status': new_status,
                'changed_by': request.user.email,
                'changed_at': timezone.now().isoformat(),
                'notes': notes
            })
            
            payment.required_fields['status_history'] = status_history
            
            # If marking as completed, set completed_at
            if new_status == 'COMPLETED' and not payment.completed_at:
                payment.completed_at = timezone.now()
            
            payment.save()
            
            # Log status change
            PaymentLog.objects.create(
                payment=payment,
                event_type='CASH_STATUS_UPDATE',
                message=f'Cash payment status changed from {old_status} to {new_status}',
                data={
                    'old_status': old_status,
                    'new_status': new_status,
                    'changed_by': request.user.email,
                    'notes': notes
                }
            )
            
            return Response({
                'success': True,
                'message': f'Payment status updated to {new_status}',
                'payment_id': str(payment.id),
                'status': payment.status
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.exception("Error in UpdateCashPaymentStatusView")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CashPaymentDetailView(APIView):
    """Get details of a cash payment"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, payment_id):
        """Get cash payment details"""
        try:
            payment = get_object_or_404(Payment, id=payment_id, payment_method='CASH001')
            
            # Only allow admins or the payment owner to view details
            if not (request.user.is_staff or payment.user == request.user):
                return Response({
                    'success': False,
                    'message': 'Permission denied'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Format response with cash-specific details
            response_data = {
                'id': str(payment.id),
                'reference_number': f"CASH-{payment.id}",
                'amount': str(payment.amount),
                'currency': payment.currency,
                'status': payment.status,
                'customer_name': payment.customer_name,
                'customer_email': payment.customer_email,
                'customer_phone': payment.customerPhoneNumber,
                'customer_address': payment.required_fields.get('address', ''),
                'payment_reason': payment.payment_reason,
                'created_at': payment.created_at.isoformat(),
                'completed_at': payment.completed_at.isoformat() if payment.completed_at else None,
                'album_title': payment.album_title,
                'artist_name': payment.artist_name,
                'plaque_type': payment.plaque_type,
                'estimated_delivery': payment.get_estimated_delivery(),
                'status_history': payment.required_fields.get('status_history', [])
            }
            
            return Response({
                'success': True,
                'payment': response_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.exception("Error in CashPaymentDetailView")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)