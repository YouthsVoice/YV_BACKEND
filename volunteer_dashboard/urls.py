from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VolunteerEventViewSet,
    FormFieldViewSet,
    get_active_event,
    submit_form
)

router = DefaultRouter()
router.register(r'admin/events', VolunteerEventViewSet, basename='admin-events')
router.register(r'admin/fields', FormFieldViewSet, basename='admin-fields')

urlpatterns = [
    path('', include(router.urls)),

    # Public-facing endpoints
    path('events/active/', get_active_event, name='get-active-event'),
    path('submit/<uuid:event_id>/', submit_form, name='submit-form'),
]
