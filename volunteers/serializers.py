from rest_framework import serializers
from .models import VolunteerSeason

class VolunteerSeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerSeason 
        fields = '__all__'