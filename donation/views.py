from rest_framework.response import Response
from django.http import HttpResponseRedirect
from rest_framework.views import APIView
from .utils.donation_helper import create_new_donation_sheet, stop_volunteer_intake,append_to_volunteer_sheet
from rest_framework.permissions import AllowAny,IsAuthenticated
from .models import DonationSeason # Import the model
from utils.bkash_payment_middilware import bkash_genarate_token ,bkash_create_payment,bkash_execute_payment
from decouple import config
from .serializers import DonationSeasonSerializer


class StartDonationIntakeView(APIView):
    permission_classes=[AllowAny]
    
    def post(self, request):
        # Get event_name from the request data
        season_name = request.data.get('season_name')
        
        if not season_name:
            return Response({"error": "Event name is required"}, status=400)
        
        # Create a new sheet in Google Drive with the event_name and get the file ID
        file_id = create_new_donation_sheet(season_name)
        
        # Create a new DonationSeason entry with intake status set to True
        new_season = DonationSeason.objects.create(
            season_name=season_name,
            file_id=file_id,
            intake_status=True  # Set the intake as open
        )
        
        return Response({
            "message": "Donation intake started",
            "season_name": new_season.season_name,
            "file_id": new_season.file_id
        })

class StopDonationIntakeView(APIView):
    def post(self, request):
        # Get the volunteer season ID from the request
        donation_season_id = request.data.get('donation_season_id')

        if not donation_season_id:
            return Response({"error": "Volunteer season ID is required"}, status=400)

        # Fetch the volunteer season by ID
        try:
            donation_season = DonationSeason.objects.get(id=donation_season_id)
        except DonationSeason.DoesNotExist:
            return Response({"error": "Volunteer season not found"}, status=404)

        # Check if the intake is currently open
        if donation_season.intake_status:
            # Stop the volunteer intake by uploading the file to Google Drive
            file_url = stop_volunteer_intake(donation_season.file_id)
            
            # Update the intake status to False
            donation_season.intake_status = False
            donation_season.save()

            return Response({"message": "Volunteer intake stopped", "file_url": file_url})
        else:
            return Response({"error": "No active intake to stop"}, status=400)
    

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
                call_back_url = f"{base_url}/api/donate/payment/callback?token={token}&name={name}&email={data.get('email')}&phone={data.get('phone')}&ammount={data.get('ammount')}&sector={data.get('sector')}"
                create_payment = bkash_create_payment(id=token, amount=data.get('amount'), callback_url=call_back_url)
                
                if create_payment:
                    creat_payment = create_payment.replace(' ', '')
                    return Response({"url": creat_payment}, status=200)
                else:
                    return Response({"error": "Faced some error"}, status=501)
            else:
                return Response({"error": "Invalid Token"})

class BkassCallBackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Redirect immediately to loading page

        # Accessing the query parameters
        payment_id = request.query_params.get('paymentID')
        token = request.query_params.get('token')
        status = request.query_params.get('status')
        name = request.query_params.get('name')
        email = request.query_params.get('email')
        phone = request.query_params.get('phone')
        ammount = request.query_params.get('ammount')
        sector=request.query_params.get('sector')

        if status in ["failure", "cancel"]:
            # Redirecting to error page if status is failure or cancel
            error_redirect_url = f"{config('FRONTEND_URL')}/donation/error"
            return HttpResponseRedirect(error_redirect_url)

        elif status == "success":
            # Call bkash_execute_payment using the token retrieved from the URL
            execute_payment_response = bkash_execute_payment(token, payment_id)

            if execute_payment_response:
                exe_payment_status = execute_payment_response.get('statusCode')
                
                print(exe_payment_status)

                if exe_payment_status == "0000":
                    # Successful payment; proceed with volunteer registration
                    trx_id = execute_payment_response.get('trxID')
                    print(trx_id)
                    data={'name':name,'email':email,'phone':phone,'ammount':ammount,"sector":sector}
                    base_url = config('URL')
                    latest_donation_season = DonationSeason.objects.order_by('-id').first()
                    if not latest_donation_season or not latest_donation_season.intake_status:
                            return Response({"error": "Volunteer intake is currently closed"}, status=400)
                    file_id = latest_donation_season.file_id
                    success = append_to_volunteer_sheet(file_id, data)

                    if success:
                        trx_id=data.get('trx_id')
                        ammount = data.get('ammount')
                        name=data.get('name').replace(' ', '-')
                        event=data.get('event').replace(' ','-')
                        frontend_url = f"{config('FRONTEND_URL')}/dontation/success?trx_id={trx_id}&name={name}"
                        return HttpResponseRedirect(frontend_url)
                    else:
                        return Response({"error": "Failed to register volunteer"}, status=500)
                else:
                    return Response({"error": execute_payment_response}, status=500)
            else:
                return Response({"error": "Payment execution response missing"}, status=500)
        else:
            return Response({"error": "Invalid status provided"}, status=400)
class CreateVolentierViwe(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        phone = request.data.get('phone')
        ammount=request.data.get('ammount')
        data={'name':name,'email':email,'phone':phone,'ammount':ammount}


        latest_donation_season = DonationSeason.objects.order_by('-id').first()
        if not latest_donation_season or not latest_donation_season.intake_status:
                    return Response({"error": "Volunteer intake is currently closed"}, status=400)

        # Validate incoming data (Recommended)
        file_id = latest_donation_season.file_id
        success = append_to_volunteer_sheet(file_id, data)

        if success:
            trx_id=data.get('trx_id')
            name=data.get('name').replace(' ', '-')
            return Response({"msg":"Successfully"},status=200)
        else:
            return Response({"error": "Failed to register volunteer"}, status=500)
       


class DonationSeasonListView(APIView):
    permission_classes=[AllowAny]
    def get(self, request):
        seasons = DonationSeason.objects.order_by('-id')  # Latest order
        serializer = DonationSeasonSerializer(seasons, many=True)
        return Response(serializer.data)