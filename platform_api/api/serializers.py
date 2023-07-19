from rest_framework import serializers
from .models import CryptoWallet, FiatWallet

###########
#
##########
class CryptoWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = CryptoWallet
        exclude = ['user', 'id']

class FiatWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiatWallet
        exclude = ['user', 'id']

###########
# Crypto trading serializers
##########
class CryptoPurchaseSerializer(serializers.Serializer):
    """
    Serializer should be used in cases of Buying/Selling crypto
    Assets
    """
    crypto_to_purchase = serializers.CharField()
    quantity_of_crypto = serializers.DecimalField(decimal_places=8, max_digits=16)
    payment_method = serializers.CharField()
    price = serializers.DecimalField(decimal_places=8, max_digits=16)

class FundFiatWalletSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    wallet_to_deposit = serializers.CharField()