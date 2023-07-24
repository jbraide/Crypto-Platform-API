from django.contrib import admin
from api.models import FiatWallet, CryptoWallet

@admin.register(FiatWallet)
class FiatWalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'fiat_type']

@admin.register(CryptoWallet)
class CryptoWalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'wallet_type', 'balance', 'symbol']
    list_editable = ['symbol', 'balance']
