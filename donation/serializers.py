from rest_framework import serializers
from .models import DonationSeason

class DonationSeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationSeason 
        fields = '__all__'