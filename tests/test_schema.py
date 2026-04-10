import pytest
from vdr_core.schema.index import validate_metadata, LEGAL_CONTRACT_SCHEMA, CLINICAL_TRIAL_SCHEMA

def test_legal_contract_schema_valid():
    metadata = {
        'document_type': 'nda',
        'party_1': 'Acme Corp',
        'party_2': 'SipHeron VDR',
        'effective_date': '2026-03-24',
        'value_usd': 50000,
    }
    result = validate_metadata(metadata, LEGAL_CONTRACT_SCHEMA)
    assert result['valid'] is True
    assert len(result['errors']) == 0

def test_legal_contract_schema_missing_required():
    metadata = {
        'party_1': 'Acme Corp',
        'party_2': 'SipHeron VDR',
        'effective_date': '2026-03-24',
    }
    # Missing document_type
    result = validate_metadata(metadata, LEGAL_CONTRACT_SCHEMA)
    assert result['valid'] is False
    assert any('document_type' in e for e in result['errors'])

def test_legal_contract_schema_enum_validation():
    metadata = {
        'document_type': 'invalid_type',
        'party_1': 'A',
        'party_2': 'B',
        'effective_date': '2026-03-24',
    }
    result = validate_metadata(metadata, LEGAL_CONTRACT_SCHEMA)
    assert result['valid'] is False
    assert any('document_type' in e for e in result['errors'])

def test_clinical_trial_schema_pattern_valid():
    metadata = {
        'trial_id': 'CT123456',
        'document_type': 'protocol',
        'site_id': 'SITE_NY_01',
    }
    result = validate_metadata(metadata, CLINICAL_TRIAL_SCHEMA)
    assert result['valid'] is True

def test_clinical_trial_schema_invalid_pattern():
    metadata = {
        'trial_id': 'ct123', # Lowercase and too short
        'document_type': 'protocol',
        'site_id': 'SITE_NY_01',
    }
    result = validate_metadata(metadata, CLINICAL_TRIAL_SCHEMA)
    assert result['valid'] is False
    assert any('trial_id' in e for e in result['errors'])

def test_type_validation():
    # Note: Our PY implementation currently does loose date validation (converts to str)
    # but we can check if it fails for 'number'
    metadata = {
        'document_type': 'contract',
        'party_1': 'A',
        'party_2': 'B',
        'effective_date': '2026-03-24',
        'value_usd': 'not_a_number',
    }
    result = validate_metadata(metadata, LEGAL_CONTRACT_SCHEMA)
    assert result['valid'] is False
    assert any('value_usd' in e for e in result['errors'])
