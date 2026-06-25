from django.db import transaction
from .models import Account, Transaction, AuditLog

def execute_transaction(account, data):
    with transaction.atomic():
        # Prevents other processes from modifying this account until we finish
        acc = Account.objects.select_for_update().get(pk=account.pk)
        
        # Duplicate Check
        if Transaction.objects.filter(ref=data['ref']).exists():
            AuditLog.objects.create(ref=data['ref'], status='REJECTED', reason='Duplicate Reference')
            return False, "Transaction with this reference already exists."

        # Balance Logic
        if data['kind'] == 'spend':
            if acc.balance < data['points']:
                AuditLog.objects.create(ref=data['ref'], status='REJECTED', reason='Insufficient Balance')
                return False, "Insufficient balance."
            acc.balance -= data['points']
        else:
            acc.balance += data['points']

        acc.save()
        Transaction.objects.create(account=acc, **data)
        AuditLog.objects.create(ref=data['ref'], status='ACCEPTED')
        
        return True, "Success"