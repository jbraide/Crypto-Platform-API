from django.db import models
from django.contrib.auth.models import User

class FiatWallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fiat_type = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ['user', 'fiat_type']

class CryptoWallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wallet_type = models.CharField(max_length=100)
    symbol = models.CharField(max_length=100, default='')
    balance = models.DecimalField(max_digits=14, decimal_places=8)
    address = models.CharField(max_length=100)

    class Meta:
        unique_together = ['user', 'wallet_type']
