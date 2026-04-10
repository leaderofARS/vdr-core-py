from typing import Dict, Any, Union, Optional
from datetime import datetime

class MetadataSchema:
    """
    Defines a validation schema for VDR document metadata.
    """
    def __init__(self, fields: Dict[str, Dict[str, Any]]):
        self.fields = fields

def validate_metadata(metadata: Dict[str, Any], schema: MetadataSchema) -> Dict[str, Any]:
    """
    Validates a metadata dictionary against a defined schema.
    
    Args:
        metadata: The data to validate.
        schema: The MetadataSchema instance defining rules.
        
    Returns:
        Dict with 'valid' (bool) and 'errors' (list of strings).
    """
    errors = []
    
    # Check required
    for field, defs in schema.fields.items():
        if defs.get('required') and not metadata.get(field):
            errors.append(f"Required field missing: {field}")
            
    # Validate present
    for key, raw_value in metadata.items():
        defs = schema.fields.get(key)
        if not defs: continue
        
        value = str(raw_value)
        if defs.get('maxLength') and len(value) > defs['maxLength']:
            errors.append(f"{key} exceeds max length {defs['maxLength']}")
            
        if defs.get('enum') and value not in defs['enum']:
            errors.append(f"{key} must be one of: {', '.join(defs['enum'])}")
            
        import re
        if defs.get('pattern') and not re.match(defs['pattern'], value):
            errors.append(f"{key} does not match required pattern")
            
        if defs.get('type') == 'number':
            try:
                float(value)
            except ValueError:
                errors.append(f"{key} must be a number")
                
    if errors:
        return {'valid': False, 'errors': errors}
    return {'valid': True, 'errors': []}

LEGAL_CONTRACT_SCHEMA = MetadataSchema({
    'document_type': {
        'type': 'enum',
        'required': True,
        'enum': ['contract', 'nda', 'amendment', 'addendum', 'termination'],
        'description': 'The type of legal document being anchored'
    },
    'party_1': {'type': 'string', 'required': True, 'maxLength': 200, 'description': 'First party legal name'},
    'party_2': {'type': 'string', 'required': True, 'maxLength': 200, 'description': 'Second party legal name'},
    'effective_date': {'type': 'date', 'required': True, 'description': 'When the contract takes effect'},
    'expiry_date': {'type': 'date', 'description': 'When the contract expires, if applicable'},
    'value_usd': {'type': 'number', 'description': 'Monetary value of the contract in USD'},
    'jurisdiction': {'type': 'string', 'maxLength': 100, 'description': 'Legal jurisdiction for the contract'}
})

CLINICAL_TRIAL_SCHEMA = MetadataSchema({
    'trial_id': {
        'type': 'string',
        'required': True,
        'pattern': r'^[A-Z]{2}\d{6}$',
        'description': 'Formal trial ID, e.g. CT123456'
    },
    'document_type': {
        'type': 'enum',
        'required': True,
        'enum': ['protocol', 'consent', 'adverse_event', 'report', 'amendment'],
        'description': 'The phase/type of clinical documentation'
    },
    'site_id': {'type': 'string', 'required': True, 'description': 'Identifier of the clinical trial site'},
    'phase': {
        'type': 'enum',
        'enum': ['I', 'II', 'III', 'IV'],
        'description': 'Trial phase'
    }
})
