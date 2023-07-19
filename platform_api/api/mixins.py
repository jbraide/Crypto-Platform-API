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
    def create_transaction(self):
        pass

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
        self.create_transaction()
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
        self.create_transaction()
        return crypto_purchased

    def get_transaction_type(self, balance, price, crypto_to_purchase, payment_method, crypto_wallet_balance):
        if self.transaction_type == None:
            raise ValueError(
                'You forgot to set The transaction Type to either Buy or Sell')
        
        if self.transaction_type == 'buy':
            return self.process_buy( balance, price, crypto_to_purchase, payment_method, crypto_wallet_balance)
        return self.process_sell( balance, price, crypto_to_purchase, payment_method, crypto_wallet_balance)
