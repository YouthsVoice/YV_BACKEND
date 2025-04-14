from django.urls import path
from .views import TokenGenarateView,BkashPaymentCreateView,BkassCallBackView,CreateVolentierViwe,StartVolunteerIntakeView,StopVolunteerIntakeView,DonationSeasonListView

urlpatterns = [
    path("start_donation_intake/",StartVolunteerIntakeView.as_view(),name="Start taking volentiers"),
    path("stop_donation_intake/",StopVolunteerIntakeView.as_view(),name="Stop taking volentiers"),
    path("token/",TokenGenarateView.as_view(),name="Genarate token"),
    path("payment/create/",BkashPaymentCreateView.as_view(),name="Bkash Pyment Create"),
    path("payment/callback/",BkassCallBackView.as_view(),name="Bkash Bkash Call Back view"),
    path("create/",CreateVolentierViwe.as_view(),name="Create Volentier"),
    path('donation-seasons/', DonationSeasonListView.as_view(), name='volunteer_season_list'),
]