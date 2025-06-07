from django.shortcuts import render
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pesepay import Pesepay
import json
from django.http import JsonResponse
import os
from rest_framework.permissions import AllowAny
import logging

logger=logging.getLogger(__name__)

pesepay = Pesepay(settings.PESEPAY_ENCRYPTION_KEY, settings.PESEPAY_INTEGRATION_KEY)
pesepay.result_url = settings.PESEPAY_RESULT_URL
pesepay.return_url = settings.PESEPAY_RETURN_URL

class CreatePaymentView(APIView):
    def post(self, request):
        data = request.data
        try:
            payment = pesepay.create_payment(
                currency_code=data.get('currency_code'),
                payment_method=data.get('payment_method_code'),
                email=data.get('email'),
                phone_number=data.get('phone_number', ''),
                customer_name=data.get('customer_name', '')
            )
            required_fields = {'requiredFieldName': 'requiredFieldValue'}
            response = pesepay.make_seamless_payment(payment, data.get('payment_reason'), data.get('amount'), required_fields)
            
            if response.success:
                return Response({
                    'poll_url': response.pollUrl,
                    'reference_number': response.referenceNumber,
                    'redirect_url': response.redirectUrl  # Include redirect URL here
                }, status=status.HTTP_201_CREATED)
            return Response({'message': response.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CheckPaymentStatusView(APIView):

    def get(self, request, reference_number):
        try:
            response = pesepay.check_payment(reference_number)
            if response.success and response.paid:
                return Response({'status': 'Paid'}, status=status.HTTP_200_OK)
            elif response.success:
                return Response({'status': 'Unpaid'}, status=status.HTTP_200_OK)
            return Response({'message': response.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class InitiatePaymentView(APIView):
    permission_classes = [AllowAny] 
    def post(self, request):
        try:
            data = json.loads(request.body)
            amount = data.get("amount")
            currency_code = data.get("currency_code")
            payment_reason = data.get("payment_reason")

            logger.info(f"Initiating payment with amount: {amount}, currency_code: {currency_code}, payment_reason: {payment_reason}")
            if not all([amount, currency_code, payment_reason]):
                return JsonResponse({"error": "Missing required parameters."}, status=400)

            
            transaction = pesepay.create_transaction(amount, currency_code, payment_reason)
            response = pesepay.initiate_transaction(transaction)

            if response.success:
                redirect_url = response.redirectUrl
                reference_number = response.referenceNumber

               
                return JsonResponse({
                    "redirect_url": redirect_url,
                    "reference_number": reference_number,
                    
                })
            else:
                logger.error(f"Pesepay initiation failed:  {response.message}")
                return JsonResponse({"error": response.message}, status=400)

        except json.JSONDecodeError:
          
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as err:
            logger.exception("Unexected Exeption in InitiatePaymentView")
            print("Error during payment initiation:", str(err))
            return JsonResponse({"error": str(err)}, status=500)
def pesepay_return(request):
    transaction_status = request.GET.get('transactionStatus')
    reference_number = request.GET.get('referenceNumber')

  
    if transaction_status == "COMPLETED":
        message = "Payment successful! Your transaction was completed."
    else:
        message = "Payment failed or canceled. Please try again."

   
    return render(request, 'confirmation.html', {"message": message, "referenceNumber": reference_number})