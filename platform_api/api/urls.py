from django.urls import path
from .views import CreateBaseCryptoWallets

app_name = 'platform-api'

urlpatterns = [
    path('create-base-crypto-wallets/', CreateBaseCryptoWallets.as_view())    
]