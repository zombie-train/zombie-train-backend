import asyncio

import telegram
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.utils import get_telegram_bot
from invoice.models import Invoice
from invoice.serializers import InvoiceSerializer


class InvoiceViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    async def _create_invoice_link(self, invoice: dict):
        bot = get_telegram_bot()
        async with bot:
            return await bot.create_invoice_link(
                title=invoice["title"],
                description=invoice["description"],
                payload=invoice.get("payload", ""),
                provider_token="",
                currency=invoice["currency"],
                prices=[telegram.LabeledPrice(label=invoice["title"], amount=invoice["amount"])],
                photo_url=invoice.get("photo_url", ""),
                photo_width=invoice.get("photo_width", 0),
                photo_height=invoice.get("photo_height", 0),
        )
    

    def create(self, request, *args, **kwargs):
        invoice_link = asyncio.run(self._create_invoice_link(request.data))
        request.data["invoice_link"] = invoice_link
        request.data["prices"] = [{
            "label": request.data["title"],
            "amount": request.data["amount"],
        }]
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
