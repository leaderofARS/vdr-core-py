import pytest
import hashlib
import re
from vdr_core.hash.index import hash_document, is_valid_hash, normalize_hash
from vdr_core.errors.errors import ValidationError
from .known_hashes import TEST_BUFFERS, KNOWN_HASHES

@pytest.mark.asyncio
async def test_hash_document_produces_valid_hex():
    hash_val = await hash_document(TEST_BUFFERS['HELLO'])
    assert len(hash_val) == 64
    assert re.match(r'^[a-f0-9]{64}$', hash_val)

@pytest.mark.asyncio
async def test_hash_document_is_deterministic():
    hash1 = await hash_document(TEST_BUFFERS['HELLO'])
    hash2 = await hash_document(TEST_BUFFERS['HELLO'])
    assert hash1 == hash2
    assert hash1 == KNOWN_HASHES['HELLO_WORLD']

@pytest.mark.asyncio
async def test_hash_matches_standard_library():
    expected = hashlib.sha256(TEST_BUFFERS['HELLO']).hexdigest()
    actual = await hash_document(TEST_BUFFERS['HELLO'])
    assert actual == expected

@pytest.mark.asyncio
async def test_different_files_different_hashes():
    hash1 = await hash_document(TEST_BUFFERS['HELLO'])
    hash2 = await hash_document(TEST_BUFFERS['SIPHERON'])
    assert hash1 != hash2

@pytest.mark.asyncio
async def test_handles_binary_data():
    hash_val = await hash_document(TEST_BUFFERS['BINARY'])
    assert len(hash_val) == 64

@pytest.mark.asyncio
async def test_raises_validation_error_for_empty():
    with pytest.raises(ValidationError):
        await hash_document(TEST_BUFFERS['EMPTY'])

@pytest.mark.asyncio
async def test_raises_validation_error_for_none():
    with pytest.raises(ValidationError):
        await hash_document(None)

def test_is_valid_hash():
    valid = 'a' * 64
    assert is_valid_hash(valid) is True
    assert is_valid_hash('too-short') is False
    assert is_valid_hash('z' * 64) is False # non-hex
    assert is_valid_hash('A' * 64) is True # Case-insensitive check

def test_normalize_hash():
    upper = 'A' * 64
    assert normalize_hash(upper) == 'a' * 64
    assert normalize_hash('  ' + 'f' * 64 + '  ') == 'f' * 64
