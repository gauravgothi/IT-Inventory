from rest_framework import serializers
from orders.serializers import OrderSerializer
from .models import Equipment

class EquipmentSerializer(serializers.ModelSerializer):
    order = OrderSerializer()
    class Meta:
        model = Equipment
        fields = '__all__'