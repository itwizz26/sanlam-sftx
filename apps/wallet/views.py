import csv
import io
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .services import execute_transaction
from apps.accounts.permissions import IsOwnerOrAdmin
from rest_framework.permissions import IsAdminUser
from .serializers import TransactionSerializer, AccountSerializer
from .services import execute_transaction
from .models import Transaction, Account
from decimal import Decimal, InvalidOperation

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

class BatchTransactionView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file provided"}, status=400)

        decoded_file = file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)

        summary = {"processed": 0, "accepted": 0, "rejected": 0, "errors": []}

        for row in reader:
            summary["processed"] += 1
            
            # Fetch the account instance first
            try:
                account_instance = Account.objects.get(pk=row['account_id'])
                
                # Convert points to Decimal
                points_decimal = Decimal(row['points'])
                
            except (Account.DoesNotExist, InvalidOperation, ValueError):
                summary["rejected"] += 1
                summary["errors"].append({"ref": row['ref'], "reason": "Invalid account or points format"})
                continue

            success, message = execute_transaction(
                account=account_instance, 
                data={
                    "ref": row['ref'],
                    "kind": row['kind'],
                    "points": points_decimal, # Pass the Decimal object
                    "occurred_at": row['occurred_at']
                }
            )
            
            if success:
                summary["accepted"] += 1
            else:
                summary["rejected"] += 1
                summary["errors"].append({"ref": row['ref'], "reason": message})

        return Response(summary)