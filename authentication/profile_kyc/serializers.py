from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import UserProfile, KYC


# Account Management Serializers
class CreateUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password',)
    
    def validate_email(self, value):
        """
        Custom validation method to check if the email is unique.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_password(self, value):
        return make_password(value)

class ChangePasswordSerializer(serializers.Serializer):
    """
    serializer  to handle Password Change
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

# KYC Management Serializers
class KYCSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = KYC
        fields = ('proof_of_address', 'document_type', 'identification_documents',)

# Profile Management Serializers
class UserProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserProfile
        exclude = ('user', )
