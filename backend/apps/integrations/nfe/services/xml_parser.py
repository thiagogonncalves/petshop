"""
NF-e XML parser - extract items from NFe/infNFe/det/prod.
Maps: xProd, qCom (fallback qTrib), vUnCom (fallback vUnTrib), vProd, cEAN, uCom (fallback uTrib).
"""
import xml.etree.ElementTree as ET
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Any

# Namespace comum em NF-e
NS = {
    'nfe': 'http://www.portalfiscal.inf.br/nfe',
}


def _get_text(el, default=''):
    if el is None:
        return default
    return (el.text or '').strip() or default


def _decimal(value: str) -> Decimal:
    if not value:
        return Decimal('0')
    value = value.replace(',', '.').strip()
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return Decimal('0')


def parse_nfe_xml(xml_content: bytes) -> Dict[str, Any]:
    """
    Parse NF-e XML and return dict with access_key, emit (supplier), nfe_number, items.
    Items: list of {product_name, quantity, unit, unit_cost, total_cost, gtin}.
    """
    root = ET.fromstring(xml_content)

    # Chave: infNFe > Id (ex: "NFe352101..." -> 44 chars)
    inf_nfe = root.find('.//nfe:infNFe', NS) or root.find('.//{http://www.portalfiscal.inf.br/nfe}infNFe')
    if inf_nfe is None:
        # Try without namespace
        inf_nfe = root.find('.//infNFe')
    if inf_nfe is None:
        raise ValueError("Elemento infNFe não encontrado no XML")

    access_key = inf_nfe.get('Id', '')
    if access_key.startswith('NFe'):
        access_key = access_key[3:]
    if len(access_key) != 44:
        raise ValueError("Chave de acesso da NF-e deve ter 44 caracteres")

    # Emitente (fornecedor)
    emit = inf_nfe.find('.//nfe:emit/nfe:xNome', NS) or inf_nfe.find('.//{http://www.portalfiscal.inf.br/nfe}emit/{http://www.portalfiscal.inf.br/nfe}xNome')
    if emit is None:
        emit = inf_nfe.find('.//emit/xNome')
    supplier_name = _get_text(emit)

    # Número da NF-e (ide > nNF)
    ide = inf_nfe.find('.//nfe:ide/nfe:nNF', NS) or inf_nfe.find('.//{http://www.portalfiscal.inf.br/nfe}ide/{http://www.portalfiscal.inf.br/nfe}nNF')
    if ide is None:
        ide = inf_nfe.find('.//ide/nNF')
    nfe_number = _get_text(ide)

    # Itens: det > prod (suporta XML com namespace default xmlns="http://www.portalfiscal.inf.br/nfe")
    items = []
    ns = 'http://www.portalfiscal.inf.br/nfe'

    def local_name(tag):
        if not tag or '}' not in tag:
            return tag or ''
        return tag.split('}', 1)[1]

    def find_child(parent, local_tag):
        for child in parent:
            if local_name(child.tag) == local_tag:
                return child
        return None

    def get_child_text(parent, local_tag):
        el = find_child(parent, local_tag)
        return _get_text(el)

    # Coletar det por nome local (funciona com ou sem namespace)
    dets = [el for el in inf_nfe.iter() if local_name(el.tag) == 'det']
    for det in dets:
        prod = find_child(det, 'prod')
        if prod is None:
            continue

        x_prod = get_child_text(prod, 'xProd')
        if not x_prod:
            continue

        q_com = _decimal(get_child_text(prod, 'qCom'))
        if q_com <= 0:
            q_com = _decimal(get_child_text(prod, 'qTrib'))
        if q_com <= 0:
            continue

        v_un_com = _decimal(get_child_text(prod, 'vUnCom'))
        if v_un_com <= 0:
            v_un_com = _decimal(get_child_text(prod, 'vUnTrib'))

        v_prod = _decimal(get_child_text(prod, 'vProd'))
        if v_prod <= 0 and v_un_com > 0:
            v_prod = (v_un_com * q_com).quantize(Decimal('0.01'))

        u_com = get_child_text(prod, 'uCom') or get_child_text(prod, 'uTrib') or 'UN'
        if not u_com:
            u_com = 'UN'

        c_ean = (get_child_text(prod, 'cEAN') or '').strip()
        if c_ean and c_ean.upper() in ('SEM GTIN', 'SEM GTIN ', ''):
            c_ean = None
        if c_ean == '':
            c_ean = None

        items.append({
            'product_name': x_prod,
            'quantity': q_com,
            'unit': u_com,
            'unit_cost': v_un_com,
            'total_cost': v_prod,
            'gtin': c_ean,
        })

    return {
        'access_key': access_key,
        'supplier_name': supplier_name,
        'nfe_number': nfe_number,
        'items': items,
    }
