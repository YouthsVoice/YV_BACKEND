from rest_framework import serializers
from .models import DonationSeasonSeason

class DonationSeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationSeasonSeasonSeason 
        fields = '__all__'