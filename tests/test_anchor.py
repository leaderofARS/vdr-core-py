import pytest
import re
from vdr_core.anchor.solana import prepare_anchor, map_to_anchor_result
from vdr_core.errors.errors import ValidationError
from .known_hashes import TEST_BUFFERS

@pytest.mark.asyncio
async def test_prepare_anchor_hashes_file():
    result = await prepare_anchor({'file': TEST_BUFFERS['HELLO']})
    assert len(result['hash']) == 64
    assert re.match(r'^[a-f0-9]{64}$', result['hash'])

@pytest.mark.asyncio
async def test_prepare_anchor_accepts_valid_hash():
    valid_hash = 'a' * 64
    result = await prepare_anchor({'hash': valid_hash})
    assert result['hash'] == valid_hash

@pytest.mark.asyncio
async def test_prepare_anchor_normalizes_uppercase():
    upper_hash = 'A' * 64
    result = await prepare_anchor({'hash': upper_hash})
    assert result['hash'] == upper_hash.lower()

@pytest.mark.asyncio
async def test_prepare_anchor_throws_on_missing_input():
    with pytest.raises(ValidationError):
        await prepare_anchor({})

@pytest.mark.asyncio
async def test_prepare_anchor_throws_on_invalid_hash():
    with pytest.raises(ValidationError):
        await prepare_anchor({'hash': 'too-short'})

@pytest.mark.asyncio
async def test_prepare_anchor_sets_metadata_from_name():
    result = await prepare_anchor({
        'file': TEST_BUFFERS['HELLO'],
        'name': 'Test Document'
    })
    assert result['metadata'] == 'Test Document'

def test_map_to_anchor_result():
    mock_response = {
        'id': 'test-id',
        'hash': 'a' * 64,
        'txSignature': '3xK9mPqRabcdef1234',
        'blockNumber': 123456,
        'blockTimestamp': '2026-03-16T04:36:02Z',
        'status': 'CONFIRMED',
        'metadata': 'Test Document'
    }
    result = map_to_anchor_result(mock_response)
    assert result['id'] == 'test-id'
    assert len(result['hash']) == 64
    assert result['status'] == 'confirmed'
    assert result['transactionSignature'] == '3xK9mPqRabcdef1234'
    assert 'app.sipheron.com/verify' in result['verificationUrl']

def test_map_to_anchor_result_explorer_url_devnet():
    mock_response = {'txSignature': 'sig123'}
    result = map_to_anchor_result(mock_response, 'devnet')
    assert 'cluster=devnet' in result['explorerUrl']
    assert 'sig123' in result['explorerUrl']

def test_map_to_anchor_result_status_mapping():
    assert map_to_anchor_result({'status': 'CONFIRMED'})['status'] == 'confirmed'
    assert map_to_anchor_result({'status': 'PENDING'})['status'] == 'pending'
    assert map_to_anchor_result({'status': 'FAILED'})['status'] == 'failed'
