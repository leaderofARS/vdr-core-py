import hashlib
import re
from typing import TypedDict, Optional, Any, Dict
from ..errors.errors import ValidationError

async def hash_document(buffer: bytes, options: dict = None) -> str:
    """
    Compute the SHA-256 hash of a document buffer.
    
    Args:
        buffer: Document as bytes.
        options: Optional hashing configuration.
        
    Returns:
        Lowercase hex digest of the document.
    """
    if not buffer:
        raise ValidationError("File buffer is required")
    if len(buffer) == 0:
        raise ValidationError("File buffer cannot be empty")
        
    hasher = hashlib.sha256()
    hasher.update(buffer)
    return hasher.hexdigest()

async def hash_file(file_path: str, options: dict = None) -> str:
    """
    Compute SHA-256 of a file on disk.
    """
    return await hash_file_with_progress(file_path, None, options)

async def hash_file_with_progress(file_path: str, on_progress: Optional[Any] = None, options: dict = None) -> str:
    """
    Compute SHA-256 of a file on disk with progress reporting.
    """
    import os
    if not os.path.exists(file_path):
        raise ValidationError(f"File not found: {file_path}")
        
    total_size = os.path.getsize(file_path)
    processed_size = 0
    hasher = hashlib.sha256()
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(64 * 1024), b""):
            hasher.update(chunk)
            processed_size += len(chunk)
            if on_progress:
                on_progress(processed_size, total_size)
                
    return hasher.hexdigest()

async def hash_file_stream(file_path: str, options: dict = None) -> str:
    """
    Alias for hash_file for compatibility with JS SDK streaming method naming.
    """
    return await hash_file(file_path, options)

async def hash_stream(stream, options: dict = None) -> str:
    """
    Compute hash from a readable iterator or stream.
    """
    hasher = hashlib.sha256()
    for chunk in stream:
        if isinstance(chunk, str):
            hasher.update(chunk.encode('utf-8'))
        else:
            hasher.update(chunk)
    return hasher.hexdigest()

async def hash_base64(b64_string: str, options: dict = None) -> str:
    """
    Compute hash of a base64-encoded string.
    """
    import base64
    if not b64_string:
        raise ValidationError("Valid base64 string is required")
    try:
        buffer = base64.b64decode(b64_string)
    except Exception as e:
        raise ValidationError(f"Invalid base64 string: {str(e)}") from e
        
    return await hash_document(buffer, options)

def is_valid_hash(h: str, algorithm: str = 'sha256') -> bool:
    """
    Validate that a string is a valid hex digest.
    """
    if not isinstance(h, str):
        return False
    info = get_algorithm_info(algorithm)
    if not info:
        return False
    import re
    return bool(re.match(rf'^[0-9a-f]{{{info["outputLength"]}}}$', h.lower()))

def normalize_hash(h: str) -> str:
    """
    Normalize a hash string by trimming and lowercasing.
    """
    return h.strip().lower()

def get_algorithm_info(algorithm: str):
    """
    Returns metadata about supported hashing algorithms.
    """
    info = {
        'sha256': {'bits': 256, 'outputLength': 64, 'recommended': True, 'label': 'SHA-256'},
        'sha512': {'bits': 512, 'outputLength': 128, 'recommended': True, 'label': 'SHA-512'},
        'md5':    {'bits': 128, 'outputLength': 32, 'recommended': False, 'label': 'MD5'},
    }
    return info.get(algorithm.lower())
