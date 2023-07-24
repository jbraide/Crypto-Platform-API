from django.urls import path
from .views import (
    CreateBaseCryptoWallets,
    CreateFiatWallet,
    DashboardHomeView, 
    GetCryptoMarketPriceAPI, 
    GetKlinePrices,
    BuyCryptoCurrency,
    SellCryptoCurrency,
    DepositToFiatWallet,
    PaymentStatusReturn
    )

app_name = 'platform-api'

urlpatterns = [
    # dashboard
    path('dashboard/', DashboardHomeView.as_view()),

    # wallets
    path('create-base-crypto-wallets/', CreateBaseCryptoWallets.as_view()),
    path('create-base-fiat-wallet/', CreateFiatWallet.as_view(),),

    # market information
    path('crypto-market-pricing/', GetCryptoMarketPriceAPI.as_view()),
    path('klines-pricing/',GetKlinePrices.as_view(),),

    # Crypto Trading
    path('buy-crypto/', BuyCryptoCurrency.as_view(),),
    path('sell-crypto/', SellCryptoCurrency.as_view(),),
    path('deposit/fiat/', DepositToFiatWallet.as_view()),
    path('payment-status/update/', PaymentStatusReturn.as_view()),
]