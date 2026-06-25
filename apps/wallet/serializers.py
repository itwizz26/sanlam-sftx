from rest_framework import serializers
from .models import Transaction, Account

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['ref', 'kind', 'points', 'occurred_at']

    def validate(self, data):
        return data
    
class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'user', 'balance', 'updated_at']