import httpx
import json
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any, Union

from ..types import SipHeronConfig, AnchorOptions
from ..errors.errors import (
    AuthenticationError, 
    ValidationError, 
    SipHeronError, 
    RateLimitError,
    NetworkError
)
from ..hash.index import hash_document, normalize_hash, is_valid_hash, get_algorithm_info
from ..anchor.solana import get_explorer_url

class AnchorsModule:
    """Sub-module for managing active anchors."""
    def __init__(self, client: 'SipHeron'):
        self.client = client

    async def revoke(self, anchor_id: str, options: Dict[str, Any]) -> None:
        """
        Revoke an existing anchor.
        
        Args:
            anchor_id: The ID of the anchor to revoke (anc_... or UUID).
            options: Revocation details (reason, note, supersededByAnchorId).
        """
        if not self.client.api_key:
            raise AuthenticationError("apiKey is required to revoke anchors.")
        await self.client._request('POST', f"/api/anchors/{anchor_id}/revoke", options)

    async def get_version_chain(self, anchor_id: str) -> List[Dict[str, Any]]:
        """
        Fetch the full version history/chain for a given anchor.
        """
        endpoint = f"/api/playground/chain/{anchor_id}" if not self.client.api_key else f"/api/hashes/{anchor_id}/chain"
        data = await self.client._request('GET', endpoint)
        chain = data.get('chain', [])
        return [self.client._map_anchor_response(c) for c in chain]

from ..verify.cache import VerificationCache
from ..pipeline.index import PipelineModule

class SipHeron:
    """
    Main SipHeron VDR client for the hosted platform.
    
    Hash locally, anchor globally. The client handles local document hashing 
    and interacts with the SipHeron API to record fingerprints on Solana.
    """
    def __init__(self, config: SipHeronConfig):
        self.api_key = config.get('apiKey')
        self.network = config.get('network', 'devnet')
        self.base_url = config.get('baseUrl', 'https://api.sipheron.com')
        if self.network == 'devnet' and config.get('baseUrl') is None:
            self.base_url = 'https://api-dev.sipheron.com'
        
        self.anchors = AnchorsModule(self)
        self.pipeline = PipelineModule(self)
        
        cache_config = config.get('cache', {})
        self.verify_cache = VerificationCache(cache_config) if cache_config else None
        
        self.http_client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                'Content-Type': 'application/json',
                **( {'Authorization': f"Bearer {self.api_key}", 'x-api-key': self.api_key} if self.api_key else {} )
            },
            timeout=30.0
        )

    async def _request(self, method: str, endpoint: str, data: dict = None, params: dict = None) -> dict:
        """Internal helper for API requests with error mapping."""
        try:
            resp = await self.http_client.request(method, endpoint, json=data, params=params)
            
            if resp.status_code == 429:
                retry_after = int(resp.headers.get('Retry-After', 60))
                raise RateLimitError(retry_after)
            
            if resp.status_code == 401:
                raise AuthenticationError()
                
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            try:
                err_data = e.response.json()
                msg = err_data.get('error', str(e))
                code = err_data.get('code', 'API_ERROR')
                raise SipHeronError(msg, code, e.response.status_code)
            except (json.JSONDecodeError, KeyError):
                raise SipHeronError(str(e), 'HTTP_ERROR', e.response.status_code)
        except httpx.RequestError as e:
            raise NetworkError(f"Network request failed: {str(e)}", e)

    async def anchor(self, options: AnchorOptions) -> Dict[str, Any]:
        """
        Anchors a document's fingerprint to the blockchain.
        """
        from ..anchor.solana import prepare_anchor
        params = await prepare_anchor(options)
        
        if not self.api_key and self.network != 'devnet':
            raise AuthenticationError('apiKey required for mainnet anchoring.')
            
        endpoint = '/api/playground/anchor' if not self.api_key else '/api/hashes'
        
        payload = {
            'hash': params['hash'],
            'hashAlgorithm': options.get('hashAlgorithm', 'sha256'),
            'metadata': params['metadata'],
            'previousAnchorId': options.get('previousAnchorId')
        }
        
        res = await self._request('POST', endpoint, payload)
        return self._map_anchor_response(res)

    async def verify(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifies document authenticity against the Solana blockchain.
        """
        if not options.get('file') and not options.get('hash'):
            raise ValidationError('Provide either file or hash.')
            
        algorithm = options.get('hashAlgorithm', 'sha256')
        
        if options.get('file'):
            h = await hash_document(options['file'], {'algorithm': algorithm})
        else:
            h = normalize_hash(options['hash'])
            if not is_valid_hash(h, algorithm):
                 raise ValidationError('Invalid hash format.')

        endpoint = '/api/playground/verify' if not self.api_key else '/api/verify'
        res = await self._request('POST', endpoint, {'hash': h, 'hashAlgorithm': algorithm})
        
        status = res.get('status', 'not_found').lower()
        if status == 'confirmed': status = 'authentic'

        return {
            'authentic': res.get('authentic', False),
            'status': status,
            'hash': h,
            'verifiedAt': res.get('verified_at', datetime.now().isoformat()),
            'anchor': self._map_anchor_response(res) if res.get('anchor') else None,
            'anchoredHash': res.get('anchor', {}).get('hash')
        }

    async def get_status(self, hash_or_id: str) -> Dict[str, Any]:
        """
        Fetch the current status of an anchor by its hash or ID.
        """
        normalized = hash_or_id.lower()
        endpoint = f"/api/hashes/public/{normalized}" if not self.api_key else f"/api/hashes/{normalized}/status"
        res = await self._request('GET', endpoint)
        return self._map_anchor_response(res)

    async def list(self, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List all anchors for the authenticated organization.
        """
        if not self.api_key:
            raise AuthenticationError("apiKey is required to list anchors.")
        
        res = await self._request('GET', '/api/hashes', params=options)
        records = [self._map_anchor_response({'anchor': r}) for r in res.get('records', [])]
        
        return {
            'records': records,
            'total': res.get('total', 0),
            'page': res.get('page', 1),
            'pages': res.get('pages', 1)
        }

    async def verify_hash(self, h: str) -> Dict[str, Any]:
        """Shortcut for verifying a pre-computed hash string."""
        return await self.verify({'hash': h})
        
    def _map_anchor_response(self, data: dict) -> Dict[str, Any]:
        from ..anchor.solana import map_to_anchor_result
        return map_to_anchor_result(data, self.network)

    async def close(self):
        """Close the underlying HTTP client."""
        await self.http_client.aclose()

    async def __aenter__(self): return self
    async def __aexit__(self, exc_type, exc, tb): await self.close()
