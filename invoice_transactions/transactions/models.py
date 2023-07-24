from uuid import uuid4
from django.db import models
from django.contrib.auth.models import User


class Transactions(models.Model):
    transaction_types = (
        ('Deposit', 'Deposit'),
        ('Buy', 'Buy'),
        ('Sell', 'Sell'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.UUIDField(default=uuid4, primary_key=True)
    type_of_transaction = models.CharField(max_length=20, \
                                           choices=transaction_types)
    status = models.CharField(max_length=30)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_date_time = models.DateTimeField(auto_now_add=True)
    paid_date_time = models.DateTimeField(blank=True, null=True)
    # This field would represent where the money came from (crypto, Bank, etc)
    paid_from = models.CharField(max_length=100)
    # The wallet (either coming from fiat to crypto or vice versa)
    payment_destination = models.CharField(max_length=100)
