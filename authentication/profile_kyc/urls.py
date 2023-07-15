from django.urls import path
from .views import (
    CreateUserAccountView,
    ChangeUserPasswordView,
    CreateUserProfileView,
    GetCustomerProifleView,
    CreateCustomerKYCView,
    GetKYCInformationView
)

app_name='profile-kyc'

urlpatterns = [
    # account
    path('register/', CreateUserAccountView.as_view(), name='register-user'),
    path('change-password/', ChangeUserPasswordView.as_view(), name='change-user-password'),

    # profile management
    path('profile/create/', CreateUserProfileView.as_view(), name='create-profile'),
    path('profile/user/', GetCustomerProifleView.as_view(), name='get-customer-profile-info'),

    # KYC Management
    path('kyc/create/', CreateCustomerKYCView.as_view(), name='create-kyc'),
    path('kyc/user/', GetKYCInformationView.as_view(), name='get-customer-kyc'),
]