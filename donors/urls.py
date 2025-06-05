from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DonorViewSet
from .views import register_donor, login_donor, get_donor_profile, get_sheet_data

router = DefaultRouter()
router.register(r'donors', DonorViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', register_donor),
    path('login/', login_donor),
    path('me/', get_donor_profile),
    path('sheet/', get_sheet_data),
]