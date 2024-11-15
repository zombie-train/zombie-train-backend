from django.contrib import admin

from invoice.models import Invoice, Transaction

# Register your models here.
admin.site.register(Invoice)
admin.site.register(Transaction)