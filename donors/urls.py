from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DonorViewSet
from .views import DonorRegisterView,DonorLoginView,BkashPaymentCreateView

router = DefaultRouter()
router.register(r'donors', DonorViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', DonorRegisterView),
    path('login/', DonorLoginView),
    path('payment/create/',BkashPaymentCreateView)
]