from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # login and refresh token
    path('login/', TokenObtainPairView.as_view(), name='login-token'),
    path('refresh-token/', TokenRefreshView.as_view(), name='refresh-login-token'),

    # app routes
    path('', include('profile_kyc.urls', namespace='profile-kyc'))
]
