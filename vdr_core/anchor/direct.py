import struct
import hashlib
from typing import Dict, Any, Union
from .solana import SIPHERON_PROGRAM_ID, SOLANA_NETWORKS, get_explorer_url, estimate_anchor_cost
from ..errors.errors import ValidationError, SolanaConnectionError, TransactionError

def get_anchor_discriminator(instruction_name: str) -> bytes:
    """
    Computes the 8-byte Anchor discriminator for a given instruction name.
    """
    hasher = hashlib.sha256()
    hasher.update(f'global:{instruction_name}'.encode('utf-8'))
    return hasher.digest()[:8]

async def anchor_to_solana(options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Directly anchors a document hash to the Solana blockchain.
    Does not require a SipHeron account or API key.
    
    Args:
        options: Configuration dictionary including:
            - 'file' / 'hash': Document or pre-computed hash.
            - 'keypair': A funded Solana Keypair object.
            - 'network': 'devnet' (default) or 'mainnet'.
            - 'metadata': Optional string metadata.
            
    Returns:
        Transaction result including signature and PDA.
    """
    from solana.rpc.async_api import AsyncClient
    from solders.pubkey import Pubkey
    from solders.transaction import VersionedTransaction
    from solders.message import MessageV0
    from solders.instruction import Instruction, AccountMeta
    from solders.system_program import ID as SYS_PROGRAM_ID

    keypair = options['keypair']
    network = options.get('network', 'devnet')
    metadata = options.get('metadata', 'Direct Anchor via vdr-core')
    custom_program_id = options.get('programId')
    rpc_url = options.get('rpcUrl') or SOLANA_NETWORKS.get(network)

    if not options.get('hash') and not options.get('buffer'):
        raise ValidationError('Must provide either a hash or file buffer')

    from ..hash.index import hash_document
    hash_string = await hash_document(options['buffer']) if options.get('buffer') else options['hash'].lower()
    hash_buffer = bytes.fromhex(hash_string)

    program_id_str = custom_program_id or SIPHERON_PROGRAM_ID[network]
    program_id = Pubkey.from_string(program_id_str)

    # Derive PDAs
    protocol_pda, _ = Pubkey.find_program_address([b'protocol_config'], program_id)
    hash_pda, _ = Pubkey.find_program_address([b'hash_record', hash_buffer, bytes(keypair.pubkey())], program_id)

    async with AsyncClient(rpc_url) as client:
        try:
            resp = await client.get_account_info(protocol_pda)
            if resp.value is None: 
                raise SolanaConnectionError('Protocol config not found on-chain. Is the program deployed?')
            
            data = resp.value.data
            # Treasury address starts at byte 48 (8 discriminator + 32 admin + 8 fee)
            treasury = Pubkey.from_bytes(data[48:80])
            
            encoded_metadata = metadata.encode('utf-8')
            metadata_len = len(encoded_metadata)
            # Layout: discriminator (8) + hash (32) + metadata_len (4) + metadata (...) + expiry (8)
            data_layout = (
                get_anchor_discriminator('register_hash') + 
                hash_buffer + 
                struct.pack('<I', metadata_len) + 
                encoded_metadata + 
                struct.pack('<Q', 0)
            )
            
            accounts = [
                AccountMeta(pubkey=hash_pda, is_signer=False, is_writable=True),
                AccountMeta(pubkey=protocol_pda, is_signer=False, is_writable=True),
                AccountMeta(pubkey=treasury, is_signer=False, is_writable=True),
                AccountMeta(pubkey=program_id, is_signer=False, is_writable=False),
                AccountMeta(pubkey=keypair.pubkey(), is_signer=True, is_writable=True),
                AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
            ]
            
            ix = Instruction(program_id=program_id, data=data_layout, accounts=accounts)
            blockhash_resp = await client.get_latest_blockhash()
            recent_blockhash = blockhash_resp.value.blockhash
            
            msg = MessageV0.try_compile(
                payer=keypair.pubkey(), 
                instructions=[ix], 
                address_lookup_table_accounts=[], 
                recent_blockhash=recent_blockhash
            )
            tx = VersionedTransaction(msg, [keypair])
            
            tx_resp = await client.send_transaction(tx)
            tx_sig = str(tx_resp.value)
            
            return {
                'hash': hash_string,
                'transactionSignature': tx_sig,
                'network': network,
                'explorerUrl': get_explorer_url(tx_sig, network),
                'cost': estimate_anchor_cost()['lamports'],
                'pda': str(hash_pda)
            }
        except Exception as e:
            if isinstance(e, (ValidationError, SolanaConnectionError)):
                raise e
            raise TransactionError(f'Failed to broadcast transaction: {str(e)}')
