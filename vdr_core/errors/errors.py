class SipHeronError(Exception):
    """Base error class for all SipHeron errors."""
    def __init__(self, message: str, code: str, status_code: int = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code

class AuthenticationError(SipHeronError):
    """Thrown when the API key is missing, invalid, or revoked."""
    def __init__(self, message: str = "Invalid or missing API key."):
        super().__init__(message, "AUTHENTICATION_ERROR", 401)

class AnchorNotFoundError(SipHeronError):
    """Thrown when no anchor record is found for the given hash."""
    def __init__(self, hash_str: str):
        super().__init__(
            f"No anchor record found for hash: {hash_str[:16]}...",
            "ANCHOR_NOT_FOUND",
            404
        )
        self.hash = hash_str

class HashMismatchError(SipHeronError):
    """Thrown when the document hash does not match the anchored hash."""
    def __init__(self, computed_hash: str, anchored_hash: str):
        super().__init__(
            "Document hash does not match anchor record. The document may have been modified.",
            "HASH_MISMATCH"
        )
        self.computed_hash = computed_hash
        self.anchored_hash = anchored_hash

class NetworkError(SipHeronError):
    """Thrown when a network request fails."""
    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message, "NETWORK_ERROR")
        self.original_error = original_error

class RateLimitError(SipHeronError):
    """Thrown when the API rate limit is exceeded."""
    def __init__(self, retry_after: int, plan: str = None):
        super().__init__(
            f"Rate limit exceeded. Retry after {retry_after} seconds.",
            "RATE_LIMIT_ERROR",
            429
        )
        self.retry_after = retry_after
        self.plan = plan
        self.upgrade_url = "https://app.sipheron.com/dashboard/billing"

class ValidationError(SipHeronError):
    """Thrown when request parameters are invalid."""
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR", 400)

class AnchorRevokedError(SipHeronError):
    """Thrown when an anchor has been revoked."""
    def __init__(self, hash_str: str, revoked_at: str = None, reason: str = None):
        super().__init__(
            f"Anchor for hash {hash_str[:16]}... has been revoked.",
            "ANCHOR_REVOKED"
        )
        self.hash = hash_str
        self.revoked_at = revoked_at
        self.reason = reason

class QuotaExceededError(SipHeronError):
    """Thrown when the monthly quota is exceeded."""
    def __init__(self, used: int, limit: int, reset_at: str):
        super().__init__(
            f"Monthly anchor quota exceeded ({used}/{limit}). Resets at {reset_at}.",
            "QUOTA_EXCEEDED",
            429
        )
        self.used = used
        self.limit = limit
        self.reset_at = reset_at
        self.upgrade_url = "https://app.sipheron.com/dashboard/billing"

class SolanaConnectionError(SipHeronError):
    """Thrown when connecting to a Solana RPC node fails."""
    def __init__(self, message: str):
        super().__init__(message, "SOLANA_CONNECTION_ERROR", 503)

class TransactionError(SipHeronError):
    """Thrown when a direct on-chain Solana transaction fails or is rejected."""
    def __init__(self, message: str):
        super().__init__(message, "TRANSACTION_ERROR", 400)
