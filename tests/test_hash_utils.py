import pytest
from vdr_core.hash.utils import hex_to_buffer, buffer_to_hex, constant_time_compare, format_file_size, truncate_hash

def test_hex_buffer_roundtrip():
    hex_str = 'a3f4b2c1d8e9f0a1'
    buf = hex_to_buffer(hex_str)
    assert buffer_to_hex(buf) == hex_str

def test_constant_time_compare():
    assert constant_time_compare('abc', 'abc') is True
    assert constant_time_compare('abc', 'abd') is False
    assert constant_time_compare('ab', 'abc') is False
    assert constant_time_compare('', '') is True
    assert constant_time_compare('ABC', 'abc') is False

def test_format_file_size():
    # Note: math.log(1024)/math.log(1024) is 1.0, so 1024 -> '1.00 KB'
    assert format_file_size(500) == '500.00 B'
    assert format_file_size(1024) == '1.00 KB'
    assert format_file_size(1024 * 1024) == '1.00 MB'
    assert format_file_size(0) == '0 B'

def test_truncate_hash():
    full = 'a' * 64
    assert truncate_hash(full, 8) == 'aaaaaaaa...aaaaaaaa'
    assert truncate_hash('abc', 8) == 'abc'
