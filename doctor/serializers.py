from rest_framework import serializers
from .models import doctor

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = doctor
        fields = '__all__'
