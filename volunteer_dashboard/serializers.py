from rest_framework import serializers
from .models import VolunteerEvent, FormField, VolunteerSubmission


class FormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormField
        fields = [
            'id',
            'event',
            'label',
            'field_type',
            'required',
            'options',
            'order',
        ]
        read_only_fields = ['id']


class VolunteerEventSerializer(serializers.ModelSerializer):
    fields = FormFieldSerializer(many=True, read_only=True)

    class Meta:
        model = VolunteerEvent
        fields = [
            'id',
            'title',
            'description',
            'status',
            'start_date',
            'end_date',
            'created_at',
            'updated_at',
            'fields',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class VolunteerSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerSubmission
        fields = [
            'id',
            'event',
            'data',
            'submitted_at',
        ]
        read_only_fields = ['id', 'submitted_at']
