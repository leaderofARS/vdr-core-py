import hmac
import math

def hex_to_buffer(hex_str: str) -> bytes:
    return bytes.fromhex(hex_str)

def buffer_to_hex(buffer: bytes) -> str:
    return buffer.hex()

def constant_time_compare(a: str, b: str) -> bool:
    if len(a) != len(b):
        return False
    return hmac.compare_digest(a, b)

def format_file_size(bytes_val: int) -> str:
    if bytes_val == 0:
        return '0 B'
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    i = int(math.floor(math.log(bytes_val) / math.log(1024)))
    return f"{(bytes_val / math.pow(1024, i)):.2f} {units[i]}"

def truncate_hash(hash_str: str, chars: int = 8) -> str:
    if len(hash_str) <= chars * 2 + 3:
        return hash_str
    return f"{hash_str[:chars]}...{hash_str[-chars:]}"
