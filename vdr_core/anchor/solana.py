from typing import Dict, Any, Union, Optional
from ..hash.index import hash_document, is_valid_hash, normalize_hash
from ..errors.errors import ValidationError

SIPHERON_CONTRACT_BASE58 = '6ecWPUK87zxwZP2pARJ75wbpCka92mYSGP1szrJxzAwo'
SIPHERON_CONTRACT = SIPHERON_CONTRACT_BASE58
SIPHERON_PROGRAM_ID = {
    'devnet': SIPHERON_CONTRACT_BASE58,
    'mainnet': SIPHERON_CONTRACT_BASE58
}
ANCHOR_SEED = 'anchor'
PROTOCOL_VERSION = 1
MAX_BATCH_SIZE = 500
HASH_LENGTH = 64
CONFIRMATION_DEPTH = 32

SOLANA_NETWORKS = {
    'devnet': 'https://api.devnet.solana.com',
    'mainnet': 'https://api.mainnet.solana.com'
}

EXPLORER_URLS = {
    'devnet': {
        'tx': lambda sig: f'https://explorer.solana.com/tx/{sig}?cluster=devnet'
    },
    'mainnet': {
        'tx': lambda sig: f'https://explorer.solana.com/tx/{sig}'
    }
}

def get_explorer_url(tx_signature: str, network: str = 'devnet') -> str:
    """
    Generate a Solana Explorer URL for a given transaction signature.
    """
    if network == 'devnet':
        return EXPLORER_URLS['devnet']['tx'](tx_signature)
    return EXPLORER_URLS['mainnet']['tx'](tx_signature)

def is_valid_tx_signature(sig: str) -> bool:
    """
    Basic validation for a Solana transaction signature.
    """
    return isinstance(sig, str) and 43 <= len(sig) <= 128

def estimate_anchor_cost() -> dict:
    """
    Returns an estimate of the Solana transaction cost for a single anchor.
    """
    return {
        'lamports': 5000,
        'sol': 0.000005,
        'usdApprox': '< $0.01'
    }

async def prepare_anchor(options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes anchoring options and computes hash if needed.
    """
    if not options.get('file') and not options.get('hash'):
        raise ValidationError('Must provide either file (bytes) or hash (string).')
    
    if options.get('file') and options.get('hash'):
        raise ValidationError("Provide either 'file' or 'hash', not both.")
    
    algorithm = options.get('hashAlgorithm', 'sha256')
    
    if options.get('file'):
        h = await hash_document(options['file'], {'algorithm': algorithm})
    else:
        h = normalize_hash(options['hash'])
        if not is_valid_hash(h, algorithm):
             raise ValidationError(f'Invalid hash format for {algorithm}.')
             
    return {
        'hash': h,
        'metadata': options.get('name') or (options.get('metadata') or {}).get('name')
    }

def map_to_anchor_result(data: Dict[str, Any], network: str = 'devnet') -> Dict[str, Any]:
    """
    Maps a raw API response to a structured SipHeron AnchorResult.
    """
    anchor = data.get('anchor', data.get('record', data))
    blockchain = data.get('blockchain', {})
    h = anchor.get('hash', '')
    tx = anchor.get('txSignature', blockchain.get('txSignature', ''))
    
    return {
        'id': anchor.get('id', ''),
        'hash': h,
        'hashAlgorithm': anchor.get('hashAlgorithm', 'sha256'),
        'transactionSignature': tx,
        'blockNumber': int(anchor.get('blockNumber', blockchain.get('blockNumber', 0))),
        'timestamp': str(anchor.get('blockTimestamp', anchor.get('createdAt', ''))),
        'verificationUrl': f"https://app.sipheron.com/verify/{h}" if h else "",
        'explorerUrl': get_explorer_url(tx, network) if tx else "",
        'status': anchor.get('status', 'pending').lower(),
        'name': str(anchor.get('metadata', '')),
        'contractAddress': SIPHERON_CONTRACT_BASE58,
        'network': network
    }
