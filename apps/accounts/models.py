from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.apps import apps

class User(AbstractUser):
    class Meta:
        swappable = 'AUTH_USER_MODEL'
    
    pass 

    @property
    def is_member(self):
        return not self.is_staff
    
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Account = apps.get_model('wallet', 'Account')
        Account.objects.create(user=instance)