from typing import TypedDict, Optional, Dict, Any, List

class AnchorOptions(TypedDict, total=False):
    file: Optional[bytes]
    hash: Optional[str]
    name: Optional[str]
    metadata: Optional[Dict[str, str]]
    idempotencyKey: Optional[str]
    hashAlgorithm: Optional[str]
    previousAnchorId: Optional[str]

class AnchorResult(TypedDict, total=False):
    id: str
    hash: str
    hashAlgorithm: str
    transactionSignature: str
    blockNumber: int
    timestamp: str
    verificationUrl: str
    explorerUrl: str
    status: str
    name: Optional[str]
    contractAddress: str
    network: str

class VerifyOptions(TypedDict, total=False):
    file: Optional[bytes]
    hash: Optional[str]
    hashAlgorithm: Optional[str]
    noCache: Optional[bool]

class VerificationResult(TypedDict, total=False):
    authentic: bool
    status: str
    hash: str
    verifiedAt: str
    anchor: Optional[AnchorResult]
    anchoredHash: Optional[str]
    revocation: Optional[Dict[str, Any]]

class OnChainVerificationOptions(TypedDict, total=False):
    hash: Optional[str]
    buffer: Optional[bytes]
    network: str
    rpcUrl: Optional[str]
    ownerPublicKey: Any
    programId: Optional[str]

class OnChainVerificationResult(TypedDict, total=False):
    authentic: bool
    hash: str
    pda: Optional[str]
    owner: Optional[str]
    timestamp: Optional[int]
    isRevoked: Optional[bool]
    metadata: Optional[str]

class BatchItemResult(TypedDict, total=False):
    index: int
    success: bool
    anchor: Optional[AnchorResult]
    error: Optional[str]

class BatchAnchorResult(TypedDict, total=False):
    total: int
    succeeded: int
    failed: int
    results: List[BatchItemResult]
    durationMs: int

class BatchAnchorOptions(TypedDict, total=False):
    documents: List[Dict[str, Any]]
    concurrency: Optional[int]
    onProgress: Optional[Any]
    continueOnError: Optional[bool]
    delayBetweenBatchesMs: Optional[int]
    hashAlgorithm: Optional[str]

class DirectAnchorOptions(TypedDict, total=False):
    hash: str
    keypair: Any
    network: str
    signer: Any

class DirectAnchorResult(TypedDict, total=False):
    transactionSignature: str
    hash: str
    explorerUrl: str
    network: str
    slot: int

class SipHeronConfig(TypedDict, total=False):
    apiKey: Optional[str]
    network: Optional[str]
    retries: Optional[int]
    timeoutMs: Optional[int]
    baseUrl: Optional[str]
