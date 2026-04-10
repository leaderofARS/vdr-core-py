import httpx
import json
from datetime import datetime
from typing import Union, Dict, Any

from ..hash.index import hash_document, is_valid_hash, normalize_hash

from ..errors.errors import ValidationError, NetworkError

async def verify_locally(file_or_hash: Union[bytes, str], anchor_hash: str) -> Dict[str, Any]:
    """
    Perform a standalone local verification by comparing against a known anchor hash.
    No network call is made.
    
    Args:
        file_or_hash: Document bytes or its pre-computed SHA-256 hash string.
        anchor_hash: The known anchor hash to compare against.
        
    Returns:
        Verification result dictionary.
    """
    if not anchor_hash or not is_valid_hash(normalize_hash(anchor_hash)):
        raise ValidationError('anchorHash must be a valid 64-character SHA-256 hex string')

    if isinstance(file_or_hash, bytes):
        computed_hash = await hash_document(file_or_hash)
    else:
        normalized = normalize_hash(file_or_hash)
        if not is_valid_hash(normalized):
            raise ValidationError('Invalid hash format. Must be 64 hex characters.')
        computed_hash = normalized

    return {
        'authentic': computed_hash == normalize_hash(anchor_hash),
        'computedHash': computed_hash,
        'anchorHash': normalize_hash(anchor_hash)
    }

async def verify_hash_standalone(
    hash_str: str,
    api_base_url: str = 'https://api.sipheron.com'
) -> Dict[str, Any]:
    """
    Calls the SipHeron public verification API without authentication.
    Use this for simple hash lookups without initializing a full client.
    
    Args:
        hash_str: 64-character SHA-256 hash.
        api_base_url: Optional API base URL override.
    """
    normalized = normalize_hash(hash_str)
    if not is_valid_hash(normalized):
        raise ValidationError('Invalid hash format. Must be a 64-character SHA-256 hex string.')

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{api_base_url}/api/verify",
                json={'hash': normalized}
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.RequestError as e:
            raise NetworkError(f"Failed to connect to verification API: {str(e)}", e) from e
        except httpx.HTTPStatusError as e:
            data = e.response.json() if e.response.status_code != 404 else {'status': 'NOT_FOUND'}

    status_map = {
        'CONFIRMED': 'authentic',
        'REVOKED': 'revoked',
        'NOT_FOUND': 'not_found'
    }

    return {
        'authentic': data.get('authentic') is True,
        'status': status_map.get(data.get('status'), 'not_found'),
        'hash': normalized,
        'verifiedAt': data.get('verified_at', datetime.now().isoformat()),
        'anchor': data.get('anchor')
    }
