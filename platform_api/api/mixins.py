import requests
from uuid import uuid4
from rest_framework.response import Response
from binance.spot import Spot
from .models import CryptoWallet, FiatWallet

class BinancePackageMixin(Spot):
    def top_coins_list(self):
        return [
            {
                'coin_name': 'Bitcoin',
                'symbol': 'BTCUSDT'
            },
            {
                'coin_name': 'Ethereum',
                'symbol': 'ETHUSDT'
            },
            {
                'coin_name': 'Ripple',
                'symbol': 'XRPUSDT'
            },
            {
                'coin_name': 'LiteCoin',
                'symbol': 'LTCUSDT'
            },
            {
                'coin_name': 'Bitcoin Cash',
                'symbol': 'BCHUSDT'
            },
        ]
    
    def crypto_prices(self):
        coins = self.top_coins_list()
        symbols = [symbol['symbol'] for symbol in coins]
        
        return self.ticker_price(symbols=symbols)


class CreateTransactionMixin:
    def create_transaction(self, trans_details: dict):

        trans_data = {
            "transaction_id": str(trans_details['id']),
            "type_of_transaction": trans_details['type_of_transaction'],
            "status": "Unpaid",
            "amount": trans_details['amount'],
            "paid_from": trans_details['paid_from'],
            "payment_destination": trans_details['payment_destination']
        }
        
        headers = {
            'Authorization': f'Bearer {trans_details["jwt"]}',
            'Content-Type': 'application/json',  # Set the content type as per your API's requirements
        }
        url = 'http://transactions:2950/transaction/list-create/' # inspect the url later "transactions:2950"
        
        
        try:
            return requests.post(
            url=url,
            json=trans_data,
            headers=headers
        )
        except requests.exceptions.RequestException as e:
            return Response(
                data={
                    'error': e,
                }
            )

class BuySellPostMixin(CreateTransactionMixin, BinancePackageMixin):
    transaction_type = None # buy/sell


    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            crypto_to_purchase = serializer.validated_data['crypto_to_purchase']
            payment_method = serializer.validated_data['payment_method']
            price = serializer.validated_data['price']

            # this field would have the data submitted by the app.
            quantity_of_crypto = serializer.validated_data['quantity_of_crypto'] 
            
            try:
                fiat_wallet = FiatWallet.objects.get(fiat_type=payment_method)
            except:
                return Response(
                    {
                        'status': 'error',
                        'message': 'You Don\'t have that Wallet'
                    },
                    status=400
                )
            
            try:
                crypto_wallet_balance = CryptoWallet.objects.get(symbol=crypto_to_purchase).balance
            except:
                return Response(
                    {
                        'status': 'error',
                        'message': 'You Don\'t this Wallet'
                    },
                    status=400
                )
            
            try:
                balance = self.get_users_balance(fiat_wallet, price)
            
            except ValueError as e:
                return Response(
                    {
                        'status': 'error',
                        'message': str(e)
                    },
                    status=400
                )
            
            
            crypto_purchased = self.get_transaction_type(balance, price, crypto_to_purchase, payment_method, crypto_wallet_balance)
            return Response(
                {
                    'status': 'success',
                    'data': {
                        'message': {
                            'crypto_purchased': crypto_purchased,
                        }
                    }
                },
                status=201

            )
        else:
            return Response(
              {
                    'status': 'error',
                    'data': serializer.errors
                },
                status=400
            )
        
    def get_users_balance(self, wallet_info, amount):
        balance = wallet_info.balance

        if balance >= amount:
            return balance
        raise ValueError('Insufficient balance for the purchase.')

    def process_buy(self, balance, price, crypto_to_purchase, payment_method, crypto_wallet_balance):
        new_balance = balance - price
        
        crypto_price_dat = self.ticker_price(crypto_to_purchase)
        crypto_price =  float(crypto_price_dat['price'])
        adjusted_price = crypto_price + (crypto_price * 0)
        crypto_purchased = float(price) / adjusted_price

        # update the fiat balance
        FiatWallet.objects.filter(fiat_type=payment_method).update(balance=new_balance)

        # update the amount of coins
        updated_wallet_balance = float(crypto_wallet_balance) + crypto_purchased
        CryptoWallet.objects.filter(symbol=crypto_to_purchase).update(balance=updated_wallet_balance)

        # create a transaction through API request
        id = uuid4()
        jwt = self.request.auth
        buy_information = {
            'id':  id,
            'type_of_transaction': 'Buy',
            'amount': adjusted_price,
            "paid_from": payment_method,
            "payment_destination": crypto_to_purchase,
            "jwt": jwt,
        }
        self.create_transaction(buy_information)
        return crypto_purchased
    
    def process_sell(self, balance, price, crypto_to_purchase, payment_method, crypto_wallet_balance):
        new_balance = balance + price
        
        crypto_price_dat = self.ticker_price(crypto_to_purchase)
        crypto_price =  float(crypto_price_dat['price'])
        adjusted_price = crypto_price - (crypto_price * 0)
        crypto_purchased = float(price) / adjusted_price

        # update the fiat balance
        FiatWallet.objects.filter(fiat_type=payment_method).update(balance=new_balance)

        # update the amount of coins
        updated_wallet_balance = float(crypto_wallet_balance) - crypto_purchased
        CryptoWallet.objects.filter(symbol=crypto_to_purchase).update(balance=updated_wallet_balance)


        # create a transaction through API request
        # create a transaction through API request
        id = uuid4()
        jwt = self.request.auth
        sell_information = {
            'id':  id,
            'type_of_transaction': 'Sell',
            'amount': adjusted_price,
            "paid_from": payment_method,
            "payment_destination": crypto_to_purchase,
            "jwt": jwt,
        }
        self.create_transaction(sell_information)
        return crypto_purchased

    def get_transaction_type(self, balance, price, crypto_to_purchase, payment_method, crypto_wallet_balance):
        if self.transaction_type == None:
            raise ValueError(
                'You forgot to set The transaction Type to either Buy or Sell')
        
        if self.transaction_type == 'buy':
            return self.process_buy( balance, price, crypto_to_purchase, payment_method, crypto_wallet_balance)
        return self.process_sell( balance, price, crypto_to_purchase, payment_method, crypto_wallet_balance)
