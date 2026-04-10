import hashlib
from datetime import datetime
from typing import Dict, Any, Optional

def generate_certificate_id(anchor: Dict[str, Any]) -> str:
    """
    Generate a deterministic certificate ID from anchor data.
    The same anchor always produces the same certificate ID.
    
    Args:
        anchor: The anchor record dictionary.
    """
    h = hashlib.sha256()
    h.update((str(anchor.get('hash', '')) + str(anchor.get('timestamp', ''))).encode('utf-8'))
    return f"CERT-{h.hexdigest()[:16].upper()}"

def build_certificate_url(
    hash_str: str, 
    api_base_url: str = 'https://api.sipheron.com', 
    is_public: bool = True
) -> str:
    """
    Build the certificate download URL for a given hash.
    Served by the SipHeron platform.
    """
    path = f"/api/hashes/{hash_str}/certificate/public" if is_public else f"/api/hashes/{hash_str}/certificate"
    return f"{api_base_url}{path}?download=true"

def prepare_certificate_data(anchor: Dict[str, Any], org: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare certificate metadata from an anchor result.
    Builds the data object before rendering.
    """
    return {
        'anchor': anchor,
        'organizationName': org.get('name', ''),
        'organizationWebsite': org.get('website'),
        'organizationLogoUrl': org.get('logoUrl'),
        'issuedAt': datetime.now().isoformat() + 'Z',
        'certificateId': generate_certificate_id(anchor)
    }

def get_certificate_proof_text(organization_name: str, hash_str: str) -> str:
    """
    Returns the formal legal proof text used in certificates.
    """
    return (
        f"This certificate confirms that the document identified by the SHA-256 hash {hash_str[:16]}... "
        f"was cryptographically anchored to the Solana blockchain at the timestamp stated herein. "
        f"The anchoring was performed by {organization_name} using the SipHeron Verified Document Registry.\n\n"
        "The existence of this blockchain record proves that: (1) the anchoring party possessed a document "
        "producing this exact SHA-256 hash at the recorded timestamp; (2) the hash — and therefore the "
        "underlying document — has not been altered since anchoring, as any modification would produce "
        "a completely different hash.\n\n"
        "This certificate does not constitute legal notarization and does not imply authorship, "
        "accuracy of content, or legal validity of the underlying document."
    )
