import asyncio

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.utils import get_telegram_bot
from invoice.models import Transaction
from invoice.views import InvoiceViewSet


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


async def _refund_star_payment(user_id, telegram_payment_charge_id):
    bot = get_telegram_bot()
    async with bot:
        return await bot.refund_star_payment(user_id, telegram_payment_charge_id)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def refund(request):
    user_id = request.data.pop("userId", "")
    transaction_id = request.data.pop("transactionId", "")

    if not user_id or not transaction_id:
        return Response({
            "error": "userId and transactionId are required"
        }, status=status.HTTP_400_BAD_REQUEST)
    try:
        is_success = asyncio.run(_refund_star_payment(
            user_id=user_id,
            telegram_payment_charge_id=transaction_id
        ))
    except Exception as e:
        return Response({
            "error": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

    if is_success:
        return Response({
             "message": 'The refund to the buyer was successfully made'
        },status=status.HTTP_200_OK)
    else:
        return Response({
            "error": "Something went wrong"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def order_receipt(request):
    tg_buyer_id = request.data.pop("userId", "")
    item_id = request.data.pop("itemId", "")

    if not tg_buyer_id or not item_id:
        return Response({
            "error": "userId and itemId are required"
        }, status=status.HTTP_404_NOT_FOUND)
    
    transaction = Transaction.objects.filter(tg_buyer_id=tg_buyer_id, item_id=item_id).first()

    if transaction and not transaction.is_receipt_delivered:
        transaction.is_receipt_delivered = True
        transaction.save()

        return Response({
            "id": transaction.id,
            "buyerId": transaction.tg_buyer_id,
            "itemId": transaction.item_id,
            "price": transaction.price,
        }, status=status.HTTP_200_OK)

    return Response({
        "error": "Target transaction not found"
    }, status=status.HTTP_404_NOT_FOUND)

async def _get_star_transactions(offset=None, limit=None):
    bot = get_telegram_bot()
    async with bot:
        return await bot.get_star_transactions(
            offset=offset,
            limit=limit
        )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def purchase_history(request):
    offset = request.query_params.get("totalPass", None)
    limit = request.query_params.get("amount", None)

    if not limit:
        return Response({
            "error": "Param 'amount' is required"
        }, status=status.HTTP_404_NOT_FOUND)

    response = asyncio.run(_get_star_transactions(
        offset=offset,
        limit=limit
    ))

    return Response({
        "transactions": [t.to_dict() for t in response.transactions if t.source is not None]
    }, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def refund_history(request):
    offset = request.query_params.get("totalPass", None)
    limit = request.query_params.get("amount", None)

    if not limit:
        return Response({
            "error": "Param 'amount' is required"
        }, status=status.HTTP_404_NOT_FOUND)

    response = asyncio.run(_get_star_transactions(
        offset=offset,
        limit=limit
    ))

    return Response({
        "transactions": [t.to_dict() for t in response.transactions if t.receiver is not None]
    }, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def update_order_receipt(request):
    transaction = request.data
    Transaction.objects.create(
        item_id=transaction["invoice_payload"],
        price=transaction["total_amount"],
        tg_buyer_id=transaction["provider_payment_charge_id"].split('_')[0],
        tg_payment_id=transaction["telegram_payment_charge_id"],
    )

    return Response({
        "message": "Transaction created"
    }, status=status.HTTP_200_OK)
