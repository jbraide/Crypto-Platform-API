from rest_framework.serializers import ModelSerializer
from .models import CryptoWallet

class CryptoWalletSerializer(ModelSerializer):
    class Meta:
        model = CryptoWallet
        fields = ['wallet_type']