from rest_framework import serializers
from .models import CategorySubcategory

class CategorySubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CategorySubcategory
        fields = ['category', 'subcategory']
