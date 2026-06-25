from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from apps.wallet.models import Account, Transaction
from django.core.files.uploadedfile import SimpleUploadedFile

class WalletViewTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="member", password="password")
        self.admin = get_user_model().objects.create_superuser(username="admin", password="password", is_staff=True)
        self.client = APIClient()

    def test_account_isolation(self):
        """Verify members can only see their own account."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/wallet/accounts/')
        self.assertEqual(len(response.data), 1) # Only their own

    def test_transaction_creation_success(self):
        """Verify transactions get created."""
        self.client.force_authenticate(user=self.user)
        data = {"ref": "tx-1", "kind": "earn", "points": "100.00", "occurred_at": "2026-06-25T10:00:00Z"}
        response = self.client.post('/api/v1/wallet/transactions/', data)
        self.assertEqual(response.status_code, 201)

    def test_spend_insufficient_funds(self):
        """Verify transactions cannot be added with zero funds."""
        self.client.force_authenticate(user=self.user)
        data = {"ref": "tx-2", "kind": "spend", "points": "500.00", "occurred_at": "2026-06-25T10:00:00Z"}
        response = self.client.post('/api/v1/wallet/transactions/', data)
        self.assertEqual(response.status_code, 400)

    def test_batch_ingest_admin_only(self):
        """Verify non-admins cannot access batch endpoint."""
        self.client.force_authenticate(user=self.user)
        csv_content = b"ref,account_id,kind,points,occurred_at\ntx-99,1,earn,10,2026-06-25T10:00:00Z"
        file = SimpleUploadedFile("test.csv", csv_content)
        response = self.client.post('/api/v1/wallet/batch-ingest/', {'file': file}, format='multipart')
        self.assertEqual(response.status_code, 403)

    def test_batch_ingest_success(self):
        """Verify batch ingestion."""
        self.client.force_authenticate(user=self.admin)
        account = Account.objects.get(user=self.user)
        csv_content = f"ref,account_id,kind,points,occurred_at\ntx-100,{account.pk},earn,50.00,2026-06-25T10:00:00Z".encode()
        file = SimpleUploadedFile("test.csv", csv_content)
        response = self.client.post('/api/v1/wallet/batch-ingest/', {'file': file}, format='multipart')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['accepted'], 1)