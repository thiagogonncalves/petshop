"""
Validação da chave de acesso NF-e (44 dígitos).
"""
import re


def normalize_access_key(key: str) -> str:
    """Remove caracteres não numéricos; retorna string vazia se não tiver 44 dígitos."""
    if not key or not isinstance(key, str):
        return ''
    digits = re.sub(r'\D', '', key.strip())
    return digits if len(digits) == 44 else ''


def validate_access_key(key: str) -> str:
    """
    Valida e retorna a chave normalizada.
    Levanta ValueError se inválida.
    """
    normalized = normalize_access_key(key)
    if not normalized:
        raise ValueError('Chave de acesso deve ter exatamente 44 dígitos.')
    return normalized
