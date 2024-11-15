from django.urls import path, include

from invoice import views, unigram_views
from rest_framework.routers import DefaultRouter
router = DefaultRouter()


router.register(r'invoice', views.InvoiceViewSet)
router.register(r'transaction', views.TransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('create-invoice/', unigram_views.create_invoice, name='create-invoice'),
    path('refund/', unigram_views.refund, name='refund'),
]

# TODO:
"""
+ /time
+ /create-invoice 
+ /refund
- /order-receipt
- /purchase-history
- /refund-history

"""