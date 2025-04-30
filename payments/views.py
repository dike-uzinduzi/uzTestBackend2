#from django.shortcuts import render, redirect
#from pesepay import Pesepay
#from django.conf import settings

#def initiate_payment(request):
    # Initialize Pesepay
  # pesepay = Pesepay(settings.PESEPAY_INTEGRATION_KEY, settings.PESEPAY_ENCRYPTION_KEY)
   # pesepay.result_url = settings.PESEPAY_RESULT_URL
   # pesepay.return_url = settings.PESEPAY_RETURN_URL

    # Capture payment details from the request
 #   currency_code = 'USD'  # You can change this based on user's preference
 #   payment_method_code = 'MOBILE'  # This should be based on available methods (e.g., 'MOBILE', 'BANK', etc.)
  #  customer_email = request.user.email
 #   customer_phone = request.POST.get('phone_number')  # Optional
  #  customer_name = request.user.get_full_name()

    # Create a payment
  #  payment = pesepay.create_payment(currency_code, payment_method_code, customer_email, customer_phone, customer_name)

    # Optional required fields
  #  required_fields = {'fieldName': 'fieldValue'}

    # Make the payment
    #response = pesepay.make_seamless_payment(payment, 'Support Album', 10.00, required_fields)

   # if response.success:
        # Save the poll URL and reference number in your database for future checks
   #     poll_url = response.poll  Url
   #     reference_number = response.referenceNumber
   #     # Redirect the user to the success page or redirect URL for payment
   #     return redirect(response.redirectUrl)
   # else:
        # Handle errors
   #     return render(request, 'error.html', {'message': response.message})
