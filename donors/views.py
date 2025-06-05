# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Donor
from .serializers import DonorSerializer
from .utils.donation_helper import create_new_donation_sheet,append_to_volunteer_sheet
from utils.bkash_payment_middilware import bkash_genarate_token ,bkash_create_payment,bkash_execute_payment
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.http import HttpResponseRedirect
from decouple import config
import jwt
from django.conf import settings

class DonorRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        phone = request.data.get('phone')
        address = request.data.get('address')

        if not all([name, email, phone, address]):
            return Response({"error": "All fields are required"}, status=400)

        if Donor.objects.filter(email=email).exists():
            return Response({"error": "Donor with this email already exists."}, status=409)

        # Create a personal sheet for the donor
        sheet_id = create_new_donation_sheet(name)

        donor = Donor.objects.create(
            name=name,
            email=email,
            phone=phone,
            address=address,
            sheet_id=sheet_id
        )

        return Response({
            "message": "Donor registered successfully.",
            "donor": DonorSerializer(donor).data
        })

class DonorLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        phone = request.data.get('phone')

        donor = Donor.objects.filter(email=email, phone=phone).first()
        if donor:
            return Response({"message": "Login success", "donor": DonorSerializer(donor).data})
        return Response({"error": "Invalid credentials"}, status=401)
    

class TokenGenarateView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        id=request.data.get("id")
        if not id:
            return Response({"error":"NO id was provided"},status=401)
        else:

            bkash_genarate_token(id)
            return Response({"OK"},status=500)

class BkashPaymentCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data

        if not data:
            return Response({"error": "NO DATA was provided"}, status=401)
        else:
            name=request.data.get("name").replace(" ","-")
            token = bkash_genarate_token()

            if token:
                base_url = config("URL")
                call_back_url = f"{base_url}/api/donor/payment/callback?token={token}&ammount={data.get('ammount')}&d_id={data.get('d_id')}&type_of={data.get('type_of')}"
                create_payment = bkash_create_payment(id=token, amount=data.get('amount'), callback_url=call_back_url)
                
                if create_payment:
                    creat_payment = create_payment.replace(' ', '')
                    return Response({"url": creat_payment}, status=200)
                else:
                    return Response({"error": "Faced some error"}, status=501)
            else:
                return Response({"error": "Invalid Token"})

class BkashCallBackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Redirect immediately to loading page
        payment_id = request.query_params.get('paymentID')
        token = request.query_params.get('token')
        status = request.query_params.get('status')
        d_id = request.query_params.get('d_id')  # JWT token of donor
        ammount = request.query_params.get('ammount')
        type_of = request.query_params.get('type_of')

        if status in ["failure", "cancel"]:
            error_redirect_url = f"{config('FRONTEND_URL')}/donor/error"
            return HttpResponseRedirect(error_redirect_url)

        elif status == "success":
            # Call bkash_execute_payment using the token from query param
            execute_payment_response = bkash_execute_payment(token, payment_id)

            if execute_payment_response:
                exe_payment_status = execute_payment_response.get('statusCode')

                if exe_payment_status == "0000":
                    trx_id = execute_payment_response.get('trxID')

                    # Decode donor token and retrieve Donor object
                    try:
                        donor_payload = jwt.decode(d_id, settings.SECRET_KEY, algorithms=["HS256"])
                        donor_email = donor_payload.get('email')
                        if not donor_email:
                            return Response({"error": "Invalid donor token - email missing"}, status=400)

                        donor = Donor.objects.get(email=donor_email)
                    except (jwt.ExpiredSignatureError, jwt.DecodeError):
                        return Response({"error": "Invalid or expired donor token"}, status=400)
                    except Donor.DoesNotExist:
                        return Response({"error": "Donor not found"}, status=404)

                    # Get donor sheet ID and prepare data
                    file_id = donor.sheet_id
                    if not file_id or not file_id.intake_status:
                        return Response({"error": "Donations are currently closed"}, status=400)

                    data = {
                        'name': donor.name,
                        'email': donor.email,
                        'phone': donor.phone,
                        'address': donor.address,
                        'ammount': ammount,
                        'type_of':type_of,
                        'trx_id': trx_id,
                    }

                    # Append to sheet
                    success = append_to_volunteer_sheet(file_id, data)

                    if success:
                        name_slug = donor.name.replace(' ', '-')
                        frontend_url = f"{config('FRONTEND_URL')}/donor/success?trx_id={trx_id}&name={name_slug}"
                        return HttpResponseRedirect(frontend_url)
                    else:
                        return Response({"error": "Failed to log donation to sheet"}, status=500)

                else:
                    return Response({"error": execute_payment_response}, status=500)
            else:
                return Response({"error": "Payment execution response missing"}, status=500)
        else:
            return Response({"error": "Invalid status provided"}, status=400)
    
