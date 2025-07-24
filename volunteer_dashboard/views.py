from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view ,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import VolunteerEvent, FormField, VolunteerSubmission
from .serializers import (
    VolunteerEventSerializer,
    FormFieldSerializer,
    VolunteerSubmissionSerializer,
)


# ---- Admin ViewSets ----

class VolunteerEventViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = VolunteerEvent.objects.all().order_by('-created_at')
    serializer_class = VolunteerEventSerializer


class FormFieldViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = FormField.objects.all().order_by('order')
    serializer_class = FormFieldSerializer


# ---- Public APIs ----

@api_view(['GET'])
@permission_classes([AllowAny])
def get_active_event(request):
    try:
        event = VolunteerEvent.objects.get(status='open')
        serializer = VolunteerEventSerializer(event)
        return Response(serializer.data)
    except VolunteerEvent.DoesNotExist:
        return Response({"detail": "No active event."}, status=404)


@api_view(['POST'])
@permission_classes([AllowAny])
def submit_form(request, event_id):
    event = get_object_or_404(VolunteerEvent, id=event_id, status='open')
    serializer = VolunteerSubmissionSerializer(data={
        'event': str(event.id),
        'data': request.data
    })
    if serializer.is_valid():
        serializer.save()
        return Response({"detail": "Submitted successfully."}, status=201)
    return Response(serializer.errors, status=400)
