from rest_framework import serializers
from .models import Donor

class DonorSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Donor
        fields = ['id', 'name', 'email', 'phone', 'address', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        donor = Donor.objects.create_user(**validated_data)
        donor.set_password(password)
        donor.save()
        return donor
