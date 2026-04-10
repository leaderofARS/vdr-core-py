import struct
from typing import Dict, Any, Union, Optional
from solders.pubkey import Pubkey
from ..anchor.solana import SIPHERON_PROGRAM_ID, SOLANA_NETWORKS
from ..hash.index import hash_document
from ..errors.errors import ValidationError, SolanaConnectionError

def derive_anchor_address(
    hash_string: str,
    owner_public_key: Pubkey,
    network_or_id: Union[str, Pubkey]
) -> Pubkey:
    """
    Derive the Program Derived Address (PDA) for a specific anchor record.
    """
    hash_buffer = bytes.fromhex(hash_string)
    
    if isinstance(network_or_id, Pubkey):
        program_id = network_or_id
    elif isinstance(network_or_id, str) and network_or_id in SIPHERON_PROGRAM_ID:
        program_id = Pubkey.from_string(SIPHERON_PROGRAM_ID[network_or_id])
    else:
        program_id = Pubkey.from_string(str(network_or_id))

    pda, _ = Pubkey.find_program_address(
        [b'hash_record', hash_buffer, bytes(owner_public_key)],
        program_id
    )
    return pda

async def verify_on_chain(options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verify a document directly against the Solana blockchain by fetching 
    the on-chain anchor record.
    
    Args:
        options: Configuration including 'file'/'hash', 'ownerPublicKey', 'network', etc.
    """
    from solana.rpc.async_api import AsyncClient
    
    network = options.get('network', 'devnet')
    rpc_url = options.get('rpcUrl') or SOLANA_NETWORKS[network]
    owner_public_key = options.get('ownerPublicKey')
    custom_program_id = options.get('programId')

    if not options.get('hash') and not options.get('buffer'):
        raise ValidationError('Must provide either a hash or file buffer')

    if not owner_public_key:
        raise ValidationError('ownerPublicKey is required for direct on-chain verification')

    hash_string = await hash_document(options['buffer']) if options.get('buffer') else options['hash'].lower()

    owner_pk = Pubkey.from_string(owner_public_key) if isinstance(owner_public_key, str) else owner_public_key
    resolved_program_id = Pubkey.from_string(custom_program_id) if custom_program_id else Pubkey.from_string(SIPHERON_PROGRAM_ID[network])

    pda = derive_anchor_address(hash_string, owner_pk, resolved_program_id)

    async with AsyncClient(rpc_url) as client:
        try:
            resp = await client.get_account_info(pda)
            if resp.value is None:
                return {
                    'authentic': False,
                    'status': 'not_found',
                    'hash': hash_string
                }
            
            data = resp.value.data
            # Manual byte parsing fallback for on-chain state:
            # Layout: discriminator(8) + hash(32) + owner(32) + timestamp(8) + isRevoked(1) + metadata(string)
            owner_bytes = data[40:72]
            timestamp = struct.unpack('<Q', data[72:80])[0]
            is_revoked = data[80] == 1
            meta_len = struct.unpack('<I', data[81:85])[0]
            metadata = data[85:85+meta_len].decode('utf-8')

            return {
                'authentic': not is_revoked,
                'status': 'revoked' if is_revoked else 'authentic',
                'hash': hash_string,
                'pda': str(pda),
                'owner': str(Pubkey.from_bytes(owner_bytes)),
                'timestamp': timestamp,
                'isRevoked': is_revoked,
                'metadata': metadata
            }
        except Exception as e:
            if isinstance(e, ValidationError): raise e
            raise SolanaConnectionError(f"Failed to verify on chain: {str(e)}")
