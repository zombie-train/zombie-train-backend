from rest_framework.decorators import api_view, permission_classes
from invoice.views import InvoiceViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from api.utils import get_telegram_bot
import asyncio

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_invoice(request):
    """
    Reuse InvoiceViewSet's create method
    """
    # Initialize the viewset
    viewset = InvoiceViewSet(
        request=request,
        format_kwarg=None
    )

    viewset.format_kwarg = None
    viewset.kwargs = {}
    viewset.args = []

    viewset.setup(request, *viewset.args, **viewset.kwargs)

    request.data["provider_token"] = request.data.pop("providerToken", "")
    
    
    # Call the create method
    response = viewset.create(request)

    if response.status_code == status.HTTP_201_CREATED:
        return Response({
            "invoiceLink": response.data["invoice_link"],
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            "error": response.data
        }, status=response.status_code)    


async def _refund_star_payment(user_id, transaction_id):
    bot = get_telegram_bot()
    async with bot:
        return await bot.refund_invoice(user_id, transaction_id)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def refund(request):
    response = asyncio.run(_refund_star_payment(
        user_id=request.data["user_id"], 
        transaction_id=request.data["transaction_id"]
    ))

    if response.status_code == status.HTTP_200_OK:
        return Response({
             "message": 'The refund to the buyer was successfully made'
        },status=status.HTTP_200_OK)
    else:
        return Response({
            "error": response.data
        }, status=response.status_code)