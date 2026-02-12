"""
Services do módulo fiscal.
"""
from .crypto import fiscal_crypto
from .xml_parser import parse_nfe_xml_fiscal, parse_res_nfe_xml

__all__ = [
    'fiscal_crypto',
    'parse_nfe_xml_fiscal',
    'parse_res_nfe_xml',
]

# SefazDistribuicaoClient importado sob demanda (depende de zeep)
