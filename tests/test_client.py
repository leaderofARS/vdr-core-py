import pytest
from vdr_core.client.client import SipHeron
from vdr_core.errors.errors import ValidationError

def test_sipheron_constructor_defaults():
    client = SipHeron({'apiKey': 'test-key'})
    assert client.network == 'devnet'
    # Default URL for devnet should be api-dev
    assert client.base_url == 'https://api-dev.sipheron.com'

def test_sipheron_constructor_mainnet():
    client = SipHeron({'apiKey': 'test-key', 'network': 'mainnet'})
    assert client.network == 'mainnet'
    assert client.base_url == 'https://api.sipheron.com'

def test_sipheron_constructor_custom_url():
    client = SipHeron({'apiKey': 'test-key', 'baseUrl': 'https://custom.api'})
    assert client.base_url == 'https://custom.api'

@pytest.mark.asyncio
async def test_anchor_validation():
    client = SipHeron({'apiKey': 'test-key'})
    
    # Missing input
    with pytest.raises(ValidationError, match="either file"):
        await client.anchor({})
        
    # Both provided
    with pytest.raises(ValidationError, match="not both"):
        await client.anchor({'file': b'test', 'hash': 'a' * 64})
        
    # Invalid hash format
    with pytest.raises(ValidationError, match="Invalid hash format"):
        await client.anchor({'hash': 'invalid'})

@pytest.mark.asyncio
async def test_verify_validation():
    client = SipHeron({'apiKey': 'test-key'})
    
    with pytest.raises(ValidationError):
        await client.verify({})
        
    with pytest.raises(ValidationError):
        await client.verify({'hash': 'bad'})
