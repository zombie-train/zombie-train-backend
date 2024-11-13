from django.db import models
from django.conf import settings

class Status(models.TextChoices):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"

class Invoice(models.Model):
    id = models.AutoField(primary_key=True)
    invoice_link = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='invoices')
    status = models.CharField(max_length=255, choices=Status.choices, default=Status.PENDING)
    title = models.CharField(max_length=255)
    description = models.TextField()
    provider_token = models.CharField(max_length=255, blank=True, default="")
    payload = models.CharField(max_length=255, blank=True, default="")
    currency = models.CharField(max_length=3, default="XTR")
    prices = models.JSONField()
    photo_url = models.CharField(max_length=255, blank=True, default="")
    photo_width = models.IntegerField(default=0)
    photo_height = models.IntegerField(default=0)
    
