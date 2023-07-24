import json, os
import requests
from uuid import uuid4
from django.contrib.auth.models import User
from rest_framework.generics import CreateAPIView, \
    GenericAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from cryptomus import Client
from dotenv import load_dotenv

from .models import CryptoWallet, FiatWallet
from .serializers import \
    CryptoWalletSerializer, CryptoPurchaseSerializer, FiatWalletSerializer, \
    FundFiatWalletSerializer
from .mixins import BinancePackageMixin, BuySellPostMixin, CreateTransactionMixin

load_dotenv()

###########
# 
# User Crypto Management API
# 
# 
########### 
class DashboardHomeView(BinancePackageMixin, ListAPIView):
    """
    Main/Home Endpoint which displays the users info
    - User Information
    - Fiat Balance
    - Wallet Balance
    """
    permission_classes = [IsAuthenticated, ]
    queryset = CryptoWallet.objects.all()
    serializer_class = CryptoWalletSerializer

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        user = self.get_user()
        crypto_wallet =  CryptoWallet.objects.filter(user=user)
        return crypto_wallet

    def get_user(self):
        return User.objects.get(username=self.request.user)

    def get_fiat_wallet_info(self):
        return FiatWallet.objects.filter(user=self.get_user())

    def fiat_wallet_serialized(self):
        return FiatWalletSerializer(self.get_fiat_wallet_info(), many=True).data

    def list(self, request, *args, **kwargs):
        user_crypto_wallet = self.get_serializer(self.get_queryset(), many=True).data
        user_info = self.get_user()
        
        # run a query to get the markets information
        crypto_prices = self.crypto_prices()
        
        # create a loop that
        # goes throught the serialized data and 
        # matches the users wallet type address to the Market data
        # and use the price for the currency to have a usd_equivalent
        for data in user_crypto_wallet:
            for crypto in crypto_prices:
                if data['symbol'] == crypto['symbol']:
                    data['usd_balance'] =  float(data['balance']) * float(crypto['price'])
                
                else:
                    pass

        return Response(
            data={
                'user_information': {
                    'first_name': user_info.first_name,
                    'last_name': user_info.last_name,
                    'username': user_info.username,
                    'email': user_info.email,
                },
                'fiat_balance': self.fiat_wallet_serialized(),
                'crypto_wallets': user_crypto_wallet,
            }
        )

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


class CreateFiatWallet(CreateAPIView):
    serializer_class = FiatWalletSerializer
    queryset = FiatWallet.objects.all()
    permission_classes = [IsAuthenticated, ]

    def perform_create(self, serializer):
        user = self.request.user
        fiat_type = serializer.validated_data.get('fiat_type')

        # Check if the user already has a wallet with the same fiat_type
        existing_wallet = FiatWallet.objects.filter(user=user, fiat_type=fiat_type).exists()

        if existing_wallet:
            raise ValidationError(f"You already have a wallet of {fiat_type}.")

        serializer.save(user=user)
    # def post(self, request, *args, **kwargs):
    #     try:
    #         self.create_fiat_wallet(request.user)
    #     except:
    #         return Response(
    #             data={
    #             'status': 'error',
    #             'message': 'You already This wallet created',
    #         },
    #         status=400
    #         )
        
    #     return Response(
    #         data={
    #             'status': 'success',
    #             'message': 'Wallet Created'
    #         },
    #         status=201
    #     )
    
    # def create_fiat_wallet(self, user):
    #     user = User.objects.get(username=user)

    #     FiatWallet.objects.create(
    #         user=user,
    #         fiat_type='USD',
    #         balance=0.0
    #     )

    
    
###########
# 
# Crytpo market Pricing  API's
# 
# 
########### 
class GetCryptoMarketPriceAPI(BinancePackageMixin, APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        return Response(
            data={
                'coins': self.crypto_prices(),
            }
        )

class GetKlinePrices(BinancePackageMixin ,APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        return Response(
           data ={
               'prices': self.klines('BTCUSDT', '1w')
           } 
        )
    


###########
# Crypto Trading Views
###########
class BuyCryptoCurrency(BuySellPostMixin, GenericAPIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = CryptoPurchaseSerializer
    transaction_type = 'buy'

class SellCryptoCurrency(BuySellPostMixin, GenericAPIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = CryptoPurchaseSerializer
    transaction_type = 'sell'

class DepositToFiatWallet(CreateTransactionMixin, GenericAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = FundFiatWalletSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            wallet = serializer.validated_data['wallet_to_deposit']
            amount = float(serializer.validated_data['amount'])

            try:
                    fiat_wallet = FiatWallet.objects.get(fiat_type=wallet)
            except:
                return Response(
                    {
                        'status': 'error',
                        'message': 'You Don\'t have that Wallet'
                    },
                    status=400
                )
            id = uuid4()
            jwt = request.auth
            
            ''' Connect to the transactions microservice to create a transaction '''
            deposit_information = {
                'id':  id,
                'type_of_transaction': 'Deposit',
                'amount': amount,
                "paid_from": "Crypto",
                "payment_destination": "USD",
                "jwt": jwt,
            }
            try:
                trans_response = self.create_transaction(deposit_information)
            
            except requests.exceptions.RequestException as e:
                return Response(
                    data={
                        'error': e,
                    },
                    status=400,
                )

            # create the payment invoice with cryptomus
            merchant_id = os.getenv('CRYPTOMUS_MERCHANT_KEY')
            api_key = os.getenv('CRYPTOMUS_API_KEY')
            

            data = {
                'amount': str(amount),
                'currency': 'USD',
                'order_id': str(id), # replace this with a dynamic ID
                'payer_amount': str(amount + (amount * 0.1)),
                # 'url_callback': 'http://localhost:250/v1/payment-status/',
                # 'url_return': '',
                # 'lifetime': ''
            }
            payment = Client.payment(api_key, merchant_id)
            response = payment.create(data)
            
            return Response(
                {
                    'payment_response':response,
                    'trans_response': trans_response.json(),
                }, 
                status=200
            )   
        return Response(
            {
                'status': 'error',
                'data': serializer.errors
            },
            status=400
        )

class PaymentStatusReturn(GenericAPIView):
    serializer_class = None

    def post(self, request, *args, **kwargs):
        print(request.POST.dict())
        pass