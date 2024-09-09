from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username', 'password','role','status','remark','enabled','employee_number','office_name','email','mobile_no','created_by','created_on','updated_by','updated_on']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Exclude fields you don't want to include in the response
        fields_to_exclude = ['password']  # Example fields to exclude
        for field in fields_to_exclude:
            representation.pop(field, None)
        return representation

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid credentials")

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)

        # Adding custom fields to the token
        refresh['username'] = user.username
        refresh['email'] = user.email
        refresh['role'] = user.role
        refresh['mobile_no'] = user.mobile_no
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }