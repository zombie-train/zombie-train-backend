from django.urls import re_path, path, include

from invoice import views, unigram_views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'invoice', views.InvoiceViewSet)
router.register(r'transaction', views.TransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    re_path('payment/create-invoice/?$', unigram_views.create_invoice, name='create-invoice'),
    re_path('payment/refund/?$', unigram_views.refund, name='refund'),
    re_path('payment/order-receipt/?$', unigram_views.order_receipt, name='order-receipt'),
    re_path('payment/purchase-history/?$', unigram_views.purchase_history, name='purchase-history'),
    re_path('payment/refund-history/?$', unigram_views.refund_history, name='refund-history'),
    re_path('payment/update-order-receipt/?$', unigram_views.update_order_receipt, name='update-order-receipt'),
]
