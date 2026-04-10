import pytest
import os
import tempfile
from vdr_core.hash.index import hash_document, hash_file, hash_file_with_progress

@pytest.fixture
def large_test_file():
    # Create a 1MB file for testing
    fd, path = tempfile.mkstemp(suffix='.bin', prefix='vdr_test_')
    test_buffer = bytearray(1024 * 1024)
    for i in range(len(test_buffer)):
        test_buffer[i] = i % 256
    
    with os.fdopen(fd, 'wb') as f:
        f.write(test_buffer)
    
    yield path, test_buffer
    
    if os.path.exists(path):
        os.remove(path)

@pytest.mark.asyncio
async def test_hash_file_matches_hash_document(large_test_file):
    path, test_buffer = large_test_file
    expected_hash = await hash_document(test_buffer)
    stream_hash = await hash_file(path)
    assert stream_hash == expected_hash

@pytest.mark.asyncio
async def test_hash_file_with_progress(large_test_file):
    path, test_buffer = large_test_file
    expected_hash = await hash_document(test_buffer)
    
    progress_calls = []
    def on_progress(processed, total):
        progress_calls.append((processed, total))
        
    stream_hash = await hash_file_with_progress(path, on_progress)
    
    assert stream_hash == expected_hash
    assert len(progress_calls) > 0
    assert progress_calls[-1] == (1024 * 1024, 1024 * 1024)
