import hmac
import hashlib
import time
import json
from typing import Dict, Any, Optional

from ..errors import SipHeronError, ValidationError

def verify_webhook_signature(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verify a SipHeron webhook signature header.
    
    Args:
        params: Dict with 'payload', 'signature', 'secret', and optional 'options'.
    """
    payload = params.get('payload')
    signature = params.get('signature')
    secret = params.get('secret')
    options = params.get('options', {})
    tolerance = options.get('tolerance', 300)

    if not payload or not signature or not secret:
        return {'valid': False, 'expired': False}

    parts = signature.split(',')
    timestamp_str = next((p[2:] for p in parts if p.startswith('t=')), None)
    hash_val = next((p[3:] for p in parts if p.startswith('v1=')), None)

    timestamp = int(timestamp_str) if timestamp_str else 0
    if not timestamp_str and not hash_val:
        timestamp = int(time.time())

    actual_hash = hash_val or signature
    age = int(time.time()) - timestamp
    
    expired = age > tolerance if timestamp_str else False

    if expired and options.get('throwOnExpired'):
        raise SipHeronError(f"Webhook expired: {age}s old (tolerance: {tolerance}s)", "WEBHOOK_EXPIRED", 401)

    payload_str = payload.decode('utf-8') if isinstance(payload, bytes) else payload

    if timestamp_str:
        expected_hash = hmac.new(
            secret.encode('utf-8'),
            f"{timestamp}.{payload_str}".encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    else:
        expected_hash = hmac.new(
            secret.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    valid = hmac.compare_digest(actual_hash.encode('utf-8'), expected_hash.encode('utf-8'))

    if not valid:
        return {'valid': False, 'expired': expired}

    try:
        event = json.loads(payload_str)
        return {'valid': True, 'expired': expired, 'event': event}
    except Exception:
        return {'valid': True, 'expired': expired}

def parse_webhook_event(options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses and verifies a webhook payload in one step.
    Raises SipHeronError if invalid.
    """
    result = verify_webhook_signature({
        'payload': options.get('body'),
        'signature': options.get('signature'),
        'secret': options.get('secret'),
        'options': {'tolerance': options.get('tolerance', 300), 'throwOnExpired': True}
    })

    if not result.get('valid'):
        throw_code = "WEBHOOK_EXPIRED" if result.get('expired') else "WEBHOOK_SIGNATURE_INVALID"
        raise SipHeronError("Invalid webhook signature", throw_code, 401)

    if not result.get('event'):
        raise ValidationError("Webhook payload is not valid JSON")

    return result['event']

class WebhookMiddleware:
    """
    Framework-specific helpers for webhook verification.
    """
    @staticmethod
    def django(secret: str):
        def middleware(get_response):
            def wrap(request):
                # Basic representation of Django middleware
                valid = verify_webhook_signature({
                    'payload': request.body,
                    'signature': request.headers.get('x-sipheron-signature', ''),
                    'secret': secret
                }).get('valid')
                if not valid:
                    from django.http import JsonResponse
                    return JsonResponse({'error': 'Invalid signature'}, status=401)
                return get_response(request)
            return wrap
        return middleware

    @staticmethod
    def fastapi(secret: str):
        async def verify(request):
            body = await request.body()
            valid = verify_webhook_signature({
                'payload': body,
                'signature': request.headers.get('x-sipheron-signature', ''),
                'secret': secret
            }).get('valid')
            if not valid:
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail='Invalid signature')
        return verify

webhook_middleware = WebhookMiddleware()
