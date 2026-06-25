from rest_framework import viewsets, permissions
from apps.accounts.permissions import IsOwnerOrAdmin
from .models import Transaction, Account
from .serializers import TransactionSerializer, AccountSerializer
from .services import execute_transaction

class AccountViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    serializer_class = AccountSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Account.objects.all()
        return Account.objects.filter(user=self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Transaction.objects.all()
        return Transaction.objects.filter(account__user=self.request.user)

    def perform_create(self, serializer):
        execute_transaction(self.request.user.wallet, serializer.validated_data)