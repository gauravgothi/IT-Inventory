from rest_framework import serializers

from equipments.serializers import EquipmentSerializer
from .models import Assignment

class AssignmentSerializer(serializers.ModelSerializer):
    equipment = EquipmentSerializer()
    
    class Meta:
        model = Assignment
        fields = '__all__'