from django.contrib.auth.models import User
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import CryptoWallet
from .serializers import CryptoWalletSerializer


class CreateBaseCryptoWallets(GenericAPIView):
    """
    Create Wallets for 7 most popular Cryptos
    """
    serializer_class = CryptoWalletSerializer
    queryset = CryptoWallet.objects.all()
    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        try:
            self.create_crypto_wallets(request.user)
        except:
            return Response(
                data={
                'status': 'error',
                'message': 'You already Have Wallets created',
            },
            status=400
            )
        
        return Response(
            data={
                'status': 'success',
                'message': 'Wallet Created'
            },
            status=201
        )

    def create_crypto_wallets(self, user):
        user = User.objects.get(username=user)

        top_wallets = [
            'Bitcoin',
            'Ethereum',
            'Ripple',
            'LiteCoin',
            'Bitcoin Cash',
            'USD Coin',
            'USD Tether',
        ]

        wallet_objects = [
            CryptoWallet(
                user=user,
                wallet_type=wallet,
                balance=0.0, 
                address='', 
            )
            for wallet in top_wallets
        ] 
        
        CryptoWallet.objects.bulk_create(wallet_objects)
        