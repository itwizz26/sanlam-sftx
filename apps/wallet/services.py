from django.db import transaction
from .models import Account, Transaction, AuditLog
from decimal import Decimal

def execute_transaction(account, data):
    # Ensure points is a Decimal
    points = Decimal(str(data['points']))
    
    with transaction.atomic():
        acc = Account.objects.select_for_update().get(pk=account.pk)
        
        if Transaction.objects.filter(ref=data['ref']).exists():
            AuditLog.objects.create(ref=data['ref'], status='REJECTED', reason='Duplicate Reference')
            return False, "Transaction with this reference already exists."

        if data['kind'] == 'spend':
            if acc.balance < points: # Compare using the casted Decimal
                AuditLog.objects.create(ref=data['ref'], status='REJECTED', reason='Insufficient Balance')
                return False, "Insufficient balance."
            acc.balance -= points
        else:
            acc.balance += points

        acc.save()
        # Create transaction with the correctly typed points
        Transaction.objects.create(account=acc, ref=data['ref'], kind=data['kind'], 
                                   points=points, occurred_at=data['occurred_at'])
        AuditLog.objects.create(ref=data['ref'], status='ACCEPTED')
        
        return True, "Success"