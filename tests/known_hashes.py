"""
Known SHA-256 hashes for deterministic test assertions.
"""

KNOWN_HASHES = {
    # SHA-256 of the string "hello world\n"
    'HELLO_WORLD': 'a948904f2f0f479b8f8197694b30184b0d2ed1c1cd2a1ec0fb85d299a192a447',
    # SHA-256 of empty string
    'EMPTY_STRING': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    # SHA-256 of the string "SipHeron VDR"
    'SIPHERON_VDR': '54e8156b825287e02581699fba30f2956cf5723b76426a88b4885664157d6928',
    # A known valid hash format
    'VALID_FORMAT': 'a3f4b2c1d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5',
}

TEST_BUFFERS = {
    'HELLO': b'hello world\n',
    'EMPTY': b'',
    'SIPHERON': b'SipHeron VDR',
    'PDF_MAGIC': b'%PDF-1.4',
    'BINARY': bytes([0x00, 0x01, 0x02, 0xff, 0xfe, 0xfd]),
}
