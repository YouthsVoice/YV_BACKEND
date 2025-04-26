from django.urls import path
from .views import SendEMAILTOALLVIEW

urlpatterns = [
    path('send-mail/', SendEMAILTOALLVIEW.as_view(), name='send_bulk_email'),
]