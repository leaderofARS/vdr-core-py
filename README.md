# SipHeron VDR-CORE (Python SDK)

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Solana](https://img.shields.io/badge/Blockchain-Solana-black.svg?logo=solana)](https://solana.com)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg?logo=python)](https://python.org)

The official Python SDK for the **SipHeron Verified Document Registry (VDR)**. Cryptographically anchor document fingerprints to the Solana blockchain to ensure data integrity, provenance, and non-repudiation.

**"Hash Locally, Anchor Globally."** — Your sensitive data never leaves your infrastructure. Only the cryptographic hashes are sent to the blockchain.

---

## Key Features

- **Local Hashing**: Securely compute SHA-256 document fingerprints within your own environment.
- **Blockchain Anchoring**: Record document hashes on the Solana blockchain for permanent, tamper-proof proof of existence.
- **Version Control**: Manage document lifecycles with anchor superseding and revocation.
- **Verification**: Instantly check document authenticity against on-chain records.
- **Integrity Reports**: Generate professional PDF reports with embedded cryptographic proofs.
- **AI Pipeline Compliance**: Anchor AI events (retrieval, generation, PII filtering) for auditability.
- **Certificates**: Generate verifiable certificates of anchoring.

---

## Installation

```bash
pip install vdr-core
```

### Requirements
- Python 3.8+
- [httpx](https://www.python-httpx.org/) (Async HTTP client)
- [fpdf2](https://py-pdf.github.io/fpdf2/) (For PDF reports)
- [solana](https://michaelhly.github.io/solana-py/) (For blockchain interaction)

---

## Quick Start

```python
import asyncio
from vdr_core import SipHeron, hash_document

async def main():
    # 1. Initialize the client
    # Generate your API key at https://app.sipheron.com
    client = SipHeron({
        "apiKey": "your_api_key_here",
        "network": "devnet" # or 'mainnet'
    })

    # 2. Hash a document locally
    file_bytes = b"Sample document content"
    doc_hash = await hash_document(file_bytes)
    print(f"Local Hash: {doc_hash}")

    # 3. Anchor to Solana
    anchor_result = await client.anchor({
        "file": file_bytes,
        "name": "Important Contract.pdf",
        "metadata": {"department": "Legal"}
    })
    print(f"Anchored! ID: {anchor_result['id']}")
    print(f"Solana Tx: {anchor_result['transactionSignature']}")

    # 4. Verify authenticity
    verification = await client.verify({"hash": doc_hash})
    if verification['authentic']:
        print("Verification Successful: Document is authentic.")

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Detailed Usage

### Client Configuration

| Option | Type | Description |
| :--- | :--- | :--- |
| `apiKey` | `string` | Your SipHeron API Key (Required for Mainnet). |
| `network` | `string` | `devnet` (default) or `mainnet`. |
| `baseUrl` | `string` | Override the API endpoint (useful for private instances). |

```python
config = {
    "apiKey": "sk_...",
    "network": "mainnet-beta",
    "cache": {"enabled": True, "ttl": 3600}
}
client = SipHeron(config)
```

### Document Hashing
Strict SHA-256 implementation following standard practices.

```python
from vdr_core import hash_document, hash_file

# From bytes
h1 = await hash_document(b"hello world")

# From local file (recommended for large files)
h2 = await hash_file("large_report.pdf")
```

### Versioning & Revocation
Maintain a chain of custody by superseding previous revisions.

```python
# Create a new version of an existing anchor
new_anchor = await client.anchor({
    "file": updated_file_bytes,
    "previousAnchorId": "anc_original_v1_id"
})

# Revoke an old version
await client.anchors.revoke("anc_old_id", {
    "reason": "Superseded",
    "note": "Replaced by version 2.0"
})

# Fetch history
history = await client.anchors.get_version_chain("anc_latest_id")
```

### Generating PDF Reports
Create a complete audit trail for a set of documents.

```python
from vdr_core.report.pdf import generate_pdf_report, ReportOptions

options = ReportOptions(
    anchors=my_anchor_list,
    solana_network="mainnet-beta",
    program_id="vdr_program_address",
    organization_name="Acme Corp"
)

pdf_bytes = await generate_pdf_report(options)
with open("integrity_report.pdf", "wb") as f:
    f.write(pdf_bytes)
```

### AI Pipeline Event Anchoring
Record critical AI interaction events to ensure compliance with AI regulations.

```python
# Anchor a RAG retrieval event
await client.pipeline.anchor_event({
    "eventType": "retrieval",
    "sessionId": "session_123",
    "payload": {
        "query": "What is our refund policy?",
        "context_hashes": ["hash1", "hash2"]
    }
})
```

---

## Error Handling

The SDK includes specific exceptions for robust error handling:

- `AuthenticationError`: Invalid or missing API key.
- `ValidationError`: Incorrect parameters or hash format.
- `RateLimitError`: API rate limits exceeded.
- `NetworkError`: Problem connecting to the SipHeron servers.
- `SipHeronError`: General SDK error.

---

## Development & Testing

We use `pytest` for all unit and integration tests.

```bash
# Install development dependencies
pip install -e ".[test]"

# Run tests
pytest
```

---

## License

This project is licensed under the **Apache License 2.0**. See the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

---

© 2026 SipHeron VDR. Built by developers, for developers.
