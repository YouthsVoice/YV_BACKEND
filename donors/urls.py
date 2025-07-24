from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DonorRegisterView,DonorLoginView,BkashPaymentCreateView

router = DefaultRouter()

urlpatterns = [
    path('login/', DonorLoginView.as_view(), name='donor-login'),         # ✅
    path('register/', DonorRegisterView.as_view(), name='donor-register'),# ✅
    path('payment/create/', BkashPaymentCreateView.as_view(), name='bkash-payment'), # ✅
]