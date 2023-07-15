from django.db import IntegrityError
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated

from .models import UserProfile, KYC
from .serializers import (
    # Account
    CreateUserSerializer,
    ChangePasswordSerializer,

    # profile
    UserProfileSerializer,

    # kyc
    KYCSerializer,
    )


#Account Management
class CreateUserAccountView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer

class ChangeUserPasswordView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated, ]

    def update(self, request, *args, **kwargs):
        user = request.user

        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Retrieve the old and new passwords from the serializer
        old_password = serializer.validated_data.get('old_password')
        new_password = serializer.validated_data.get('new_password')
        # Check if the old password matches the user's current password
        if not user.check_password(old_password):
            return Response({'error': 'Invalid old password.'}, status=400)

        # Set the new password and save the user
        user.set_password(new_password)
        user.save()

        return Response({'success': 'Password changed successfully.'})


#Profile Management
class CreateUserProfileView(CreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, ]

    def perform_create(self, serializer):
        """
        Override perform_create to save the user
        before saving the model
        """
        user = self.request.user
        try:
            serializer.save(user=user)
        except IntegrityError:
            raise serializers.ValidationError(
                {'error': 'You have already created your profile'}
            )

        return super().perform_create(serializer)

class GetCustomerProifleView(ListAPIView):
    """
    Get the Customer Details to display
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        user = self.request.user
        profile = UserProfile.objects.filter(user=user).values()
        return profile

# KYC Management
class CreateCustomerKYCView(CreateAPIView):
    queryset = KYC
    serializer_class = KYCSerializer
    permission_classes = [IsAuthenticated, ]

    def perform_create(self, serializer):
        profile = UserProfile.objects.get(user=self.request.user)
        
        try:
            serializer.save(profile=profile)
        except IntegrityError:
            raise serializers.ValidationError(
                {'error': 'You already Have KYC submitted'}
            )
        return super().perform_create(serializer)
    
class GetKYCInformationView(ListAPIView):
    queryset = KYC.objects.all()
    serializer_class = KYCSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        profile = UserProfile.objects.get(user=self.request.user)
        kyc = KYC.objects.filter(profile=profile).values()
        return kyc
    