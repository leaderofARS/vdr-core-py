import pytest
from vdr_core.verify.verify import verify_locally
from vdr_core.hash.index import hash_document
from vdr_core.errors.errors import ValidationError
from .known_hashes import TEST_BUFFERS

@pytest.mark.asyncio
async def test_verify_locally_match():
    h = await hash_document(TEST_BUFFERS['HELLO'])
    result = await verify_locally(TEST_BUFFERS['HELLO'], h)
    assert result['authentic'] is True
    assert result['computedHash'] == h

@pytest.mark.asyncio
async def test_verify_locally_mismatch():
    h = await hash_document(TEST_BUFFERS['HELLO'])
    result = await verify_locally(TEST_BUFFERS['SIPHERON'], h)
    assert result['authentic'] is False
    assert result['computedHash'] != result['anchorHash']

@pytest.mark.asyncio
async def test_verify_locally_precomputed_hash():
    h = await hash_document(TEST_BUFFERS['HELLO'])
    result = await verify_locally(h, h)
    assert result['authentic'] is True

@pytest.mark.asyncio
async def test_verify_locally_case_insensitive():
    h = await hash_document(TEST_BUFFERS['HELLO'])
    result = await verify_locally(TEST_BUFFERS['HELLO'], h.upper())
    assert result['authentic'] is True

@pytest.mark.asyncio
async def test_verify_locally_invalid_anchor_hash():
    with pytest.raises(ValidationError):
        await verify_locally(TEST_BUFFERS['HELLO'], 'invalid')

@pytest.mark.asyncio
async def test_verify_locally_one_byte_mod():
    original = b'Important contract text'
    modified = b'Important Contract text' # capital C
    h = await hash_document(original)
    result = await verify_locally(modified, h)
    assert result['authentic'] is False
