from rest_framework import serializers
from invoice.models import Invoice

class InvoiceSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Invoice
        fields = '__all__'
