import hashlib
import hmac
import time
import base64
from rest_framework.permissions import BasePermission
from django.conf import settings


class IsValidToken(BasePermission):
    def has_permission(self, request, view):
        api_key = settings.SECURITY_API_KEY
        # token = request.data.get('token')
        token = request.query_params.get('token')

        if not token:
            return False

        try:
            # Base64 decode the token
            token_parts = base64.b64decode(token).decode().split(':')
            if len(token_parts) != 4:
                return False

            timestamp, user_id, score, signature = token_parts
        except Exception as e:
            return False

        # Check if the timestamp is within an acceptable range (e.g., 5 minutes)
        current_time = int(time.time())
        if abs(current_time - int(timestamp)) > 300:
            return False

        # Generate the expected signature
        message = f"{timestamp}{user_id}{score}"
        expected_signature = hmac.new(api_key.encode(), message.encode(),
                                      hashlib.sha256).hexdigest()

        return hmac.compare_digest(signature, expected_signature)
