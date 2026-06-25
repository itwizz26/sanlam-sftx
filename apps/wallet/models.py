from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal

class Account(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Account {self.user.username} - Balance: {self.balance}"

class Transaction(models.Model):
    KIND_CHOICES = [('earn', 'Earn'), ('spend', 'Spend')]
    
    ref = models.CharField(max_length=100, unique=True, db_index=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    kind = models.CharField(max_length=10, choices=KIND_CHOICES)
    points = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    occurred_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-occurred_at']

class AuditLog(models.Model):
    ref = models.CharField(max_length=100, db_index=True)
    status = models.CharField(max_length=20)
    reason = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)