import re

PII_PATTERNS = [
    {'regex': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', 'label': '[REDACTED_EMAIL]'},
    {'regex': r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', 'label': '[REDACTED_PHONE]'},
    {'regex': r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9][0-9])[0-9]{12})\b', 'label': '[REDACTED_CREDIT_CARD]'},
    {'regex': r'\b(?!000|666)[0-8][0-9]{2}-(?!00)[0-9]{2}-(?!0000)[0-9]{4}\b', 'label': '[REDACTED_SSN]'},
    {'regex': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b', 'label': '[REDACTED_IP]'},
    {'regex': r'\b[A-Za-z0-9+/]{40,}=*\b', 'label': '[REDACTED_API_KEY]'},
]

def redact_string(input_str: str) -> dict:
    redacted = input_str
    matches = 0
    for pattern in PII_PATTERNS:
        found = re.findall(pattern['regex'], redacted)
        if found:
            matches += len(found)
            redacted = re.sub(pattern['regex'], pattern['label'], redacted)
    return {'redacted': redacted, 'matches': matches}

def scrub_payload(obj: any) -> dict:
    state = {'piiDetected': False}

    def traverse(item):
        if isinstance(item, str):
            res = redact_string(item)
            if res['matches'] > 0:
                state['piiDetected'] = True
            return res['redacted']
        
        if isinstance(item, list):
            return [traverse(x) for x in item]
        
        if isinstance(item, dict):
            return {k: traverse(v) for k, v in item.items()}
            
        return item

    sanitized = traverse(obj)
    return {'sanitized': sanitized, 'piiDetected': state['piiDetected']}
