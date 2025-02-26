from rest_framework.response import Response
from django.http import HttpResponseRedirect
from rest_framework.views import APIView
from .utils.volunteer_helpers import create_new_volunteer_sheet, stop_volunteer_intake,append_to_volunteer_sheet
from rest_framework.permissions import AllowAny,IsAuthenticated
from .models import VolunteerSeason # Import the model
from django.shortcuts import  render
from utils.bkash_payment_middilware import bkash_genarate_token ,bkash_create_payment,bkash_execute_payment
from decouple import config
from .serializers import VolunteerSeasonSerializer
class StartVolunteerIntakeView(APIView):
    permission_classes=[AllowAny]
    
    def post(self, request):
        # Get event_name from the request data
        event_name = request.data.get('event_name')
        
        if not event_name:
            return Response({"error": "Event name is required"}, status=400)
        
        # Create a new sheet in Google Drive with the event_name and get the file ID
        file_id = create_new_volunteer_sheet(event_name)
        
        # Create a new VolunteerSeason entry with intake status set to True
        new_season = VolunteerSeason.objects.create(
            event_name=event_name,
            file_id=file_id,
            intake_status=True  # Set the intake as open
        )
        
        return Response({
            "message": "Volunteer intake started",
            "event_name": new_season.event_name,
            "file_id": new_season.file_id
        })

class StopVolunteerIntakeView(APIView):
    def post(self, request):
        # Get the volunteer season ID from the request
        volunteer_season_id = request.data.get('volunteer_season_id')

        if not volunteer_season_id:
            return Response({"error": "Volunteer season ID is required"}, status=400)

        # Fetch the volunteer season by ID
        try:
            volunteer_season = VolunteerSeason.objects.get(id=volunteer_season_id)
        except VolunteerSeason.DoesNotExist:
            return Response({"error": "Volunteer season not found"}, status=404)

        # Check if the intake is currently open
        if volunteer_season.intake_status:
            # Stop the volunteer intake by uploading the file to Google Drive
            file_url = stop_volunteer_intake(volunteer_season.file_id)
            
            # Update the intake status to False
            volunteer_season.intake_status = False
            volunteer_season.save()

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
            address=request.data.get("address").replace(" ","-")
            institution=request.data.get("institution").replace(" ","-")
            bloodgrp=request.data.get("bloodgrp")
            token = bkash_genarate_token()

            if token:
                base_url = config("URL")
                call_back_url = f"{base_url}/api/vol/payment/callback?token={token}&name={name}&email={data.get('email')}&phone={data.get('phone')}&religion={data.get('religion')}&age={data.get('age')}&tshirt_size={data.get('tshirt_size')}&address={address}&institution={institution}&bloodgrp={bloodgrp}"
                create_payment = bkash_create_payment(id=token, amount=data.get('amount'), callback_url=call_back_url)
                create_payment = create_payment.replace(' ', '')
                
                if create_payment:
                    return Response({"url": create_payment}, status=200)
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
        age = request.query_params.get('age')
        tshirt_size = request.query_params.get('tshirt_size')
        religion = request.query_params.get('religion')
        address=request.query_params.get("address")
        institution=request.query_params.get("institution")
        bloodgrp=request.query_params.get("bloodgrp")

        

        if status in ["failure", "cancel"]:
            # Redirecting to error page if status is failure or cancel
            error_redirect_url = f"{config('FRONTEND_URL')}/youthvoice/volunteer/error"
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
                    data={'name':name,'email':email,'phone':phone,'age':age,'tshirt_size':tshirt_size,'religion':religion, 'trx_id':trx_id,'bloodgrp':bloodgrp,'address':address,'institution':institution}
                    base_url = config('URL')
                    latest_volunteer_season = VolunteerSeason.objects.order_by('-id').first()
                    if not latest_volunteer_season or not latest_volunteer_season.intake_status:
                            return Response({"error": "Volunteer intake is currently closed"}, status=400)

        # Validate incoming data (Recommended)
                    required_fields = ['name', 'email', 'phone', 'age', 'tshirt_size', 'religion', 'trx_id','bloodgrp','address','institution']
                    file_id = latest_volunteer_season.file_id
                    success = append_to_volunteer_sheet(file_id, data)

                    if success:
                        trx_id=data.get('trx_id')
                        name=data.get('name').replace(' ', '-')
                        frontend_url = f"{config('FRONTEND_URL')}/youthvoice/volunteer/success?trx_id={trx_id}&name={name}"
                        return HttpResponseRedirect(frontend_url)
                    else:
                        return Response({"error": "Failed to register volunteer"}, status=500)

                    # Redirect to success page if registration succeeds
                    if response and response.status_code == 200:
                        res = response.json()
                        frontend_url = res.get("url")
                        if frontend_url:
                            return HttpResponseRedirect(frontend_url)
                        else:
                            return Response({"error": "Frontend URL missing in response"}, status=500)
                    else:
                        return Response({"error": execute_payment_response}, status=response.status_code)
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
        age = request.data.get('age')
        tshirt_size = request.data.get('tshirt_size')
        religion = request.data.get('religion')
        address=request.data.get("address")
        institution=request.data.get("institution")
        bloodgrp=request.data.get("bloodgrp")
        trx_id="qzq5qqzqzqzq5z5656"
        data={'name':name,'email':email,'phone':phone,'age':age,'tshirt_size':tshirt_size,'religion':religion, 'trx_id':trx_id,'bloodgrp':bloodgrp,'address':address,'institution':institution}


        latest_volunteer_season = VolunteerSeason.objects.order_by('-id').first()
        if not latest_volunteer_season or not latest_volunteer_season.intake_status:
                    return Response({"error": "Volunteer intake is currently closed"}, status=400)

        # Validate incoming data (Recommended)
        file_id = latest_volunteer_season.file_id
        success = append_to_volunteer_sheet(file_id, data)

        if success:
            trx_id=data.get('trx_id')
            name=data.get('name').replace(' ', '-')
            return Response({"msg":"Successfully"},status=200)
        else:
            return Response({"error": "Failed to register volunteer"}, status=500)
       


class VolunteerSeasonListView(APIView):
    permission_classes=[AllowAny]
    def get(self, request):
        seasons = VolunteerSeason.objects.order_by('-id')  # Latest order
        serializer = VolunteerSeasonSerializer(seasons, many=True)
        return Response(serializer.data)