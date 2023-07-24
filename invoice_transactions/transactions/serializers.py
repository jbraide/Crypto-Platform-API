from rest_framework import serializers
from .models import Transactions

class CreateTransactionSerializer(serializers.ModelSerializer):
    transaction_id = serializers.CharField(required=True)

    class Meta:
        model = Transactions
        exclude = ['user', 'paid_date_time']

class UpdateTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transactions
        fields = ['status', 'paid_date_time']

class ViewTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transactions
        exclude = ['user']