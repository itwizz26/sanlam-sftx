from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['ref', 'kind', 'points', 'occurred_at']

    def validate(self, data):
        return data