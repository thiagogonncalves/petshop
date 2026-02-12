"""
Parse de XML NF-e: resNFe (resumo) e procNFe/nfeProc (completo).
Extrai metadados e itens para o módulo fiscal.
"""
import gzip
import base64
import xml.etree.ElementTree as ET
from decimal import Decimal, InvalidOperation
from typing import Dict, Any, List, Optional

NS = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}


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


def _local_name(tag):
    if not tag or '}' not in tag:
        return tag or ''
    return tag.split('}', 1)[1]


def _find_child(parent, local_tag):
    for child in parent:
        if _local_name(child.tag) == local_tag:
            return child
    return None


def _get_child_text(parent, local_tag):
    el = _find_child(parent, local_tag)
    return _get_text(el)


def decode_doc_zip(doc_zip_base64: str) -> tuple[bytes, str]:
    """
    Descompacta docZip (base64 gzip) da SEFAZ.
    Retorna (xml_bytes, schema) onde schema é 'resNFe' ou 'procNFe' etc.
    """
    raw = base64.b64decode(doc_zip_base64)
    decompressed = gzip.decompress(raw)
    root = ET.fromstring(decompressed)
    schema = _local_name(root.tag)
    return decompressed, schema


def parse_res_nfe_xml(xml_content: bytes) -> Dict[str, Any]:
    """
    Parse resNFe (resumo) - retorna dict com chave, emitente, destinatário, data, valor.
    """
    root = ET.fromstring(xml_content)
    inf = root.find('.//nfe:resNFe', NS) or root.find('.//{http://www.portalfiscal.inf.br/nfe}resNFe')
    if inf is None:
        for el in root.iter():
            if _local_name(el.tag) == 'resNFe':
                inf = el
                break
    if inf is None:
        raise ValueError('Elemento resNFe não encontrado')

    ch_nfe = _get_text(inf.find('.//nfe:chNFe', NS) or _find_child(inf, 'chNFe'))
    if len(ch_nfe) != 44:
        raise ValueError('Chave inválida no resNFe')

    x_nome_emit = ''
    cnpj_emit = ''
    for el in inf.iter():
        if _local_name(el.tag) == 'xNome' and not x_nome_emit:
            x_nome_emit = _get_text(el)
        if _local_name(el.tag) == 'CNPJ' and not cnpj_emit:
            cnpj_emit = _get_text(el)

    x_nome_dest = ''
    cnpj_dest = ''
    dest = _find_child(inf, 'dest')
    if dest:
        x_nome_dest = _get_child_text(dest, 'xNome')
        cnpj_dest = _get_child_text(dest, 'CNPJ') or _get_child_text(dest, 'CPF')

    dh_emi = _get_text(
        inf.find('.//nfe:dhEmi', NS) or _find_child(inf, 'dhEmi')
    )
    v_nf = _decimal(
        _get_text(inf.find('.//nfe:vNF', NS) or _find_child(inf, 'vNF'))
    )
    c_sit = _get_text(
        inf.find('.//nfe:cSitNFe', NS) or _find_child(inf, 'cSitNFe')
    )

    return {
        'chave': ch_nfe,
        'emitente': x_nome_emit or cnpj_emit or '-',
        'emitente_cnpj': cnpj_emit,
        'destinatario': x_nome_dest or cnpj_dest or '-',
        'destinatario_cnpj': cnpj_dest,
        'data_emissao': dh_emi,
        'valor_total': str(v_nf),
        'situacao': c_sit,
    }


def parse_nfe_xml_fiscal(xml_content: bytes) -> Dict[str, Any]:
    """
    Parse NF-e completa (nfeProc ou NFe) e retorna resumo + itens.
    Itens no formato: item_number, description, ncm, cfop, qty, unit_price, total.
    """
    root = ET.fromstring(xml_content)
    inf_nfe = (
        root.find('.//nfe:infNFe', NS)
        or root.find('.//{http://www.portalfiscal.inf.br/nfe}infNFe')
        or root.find('.//infNFe')
    )
    if inf_nfe is None:
        raise ValueError('Elemento infNFe não encontrado')

    access_key = inf_nfe.get('Id', '')
    if access_key.startswith('NFe'):
        access_key = access_key[3:]
    if len(access_key) != 44:
        raise ValueError('Chave da NF-e deve ter 44 caracteres')

    emit = _find_child(inf_nfe, 'emit')
    emitente = _get_child_text(emit, 'xNome') if emit else ''
    emitente_cnpj = _get_child_text(emit, 'CNPJ') if emit else ''

    dest = _find_child(inf_nfe, 'dest')
    destinatario = _get_child_text(dest, 'xNome') if dest else ''
    if not destinatario:
        destinatario = _get_child_text(dest, 'CNPJ') or _get_child_text(dest, 'CPF') if dest else '-'

    ide = _find_child(inf_nfe, 'ide')
    dh_emi = _get_child_text(ide, 'dhEmi') if ide else ''

    total = _find_child(inf_nfe, 'total')
    v_nf = Decimal('0')
    if total:
        icms_tot = _find_child(total, 'ICMSTot')
        if icms_tot:
            v_nf = _decimal(_get_child_text(icms_tot, 'vNF'))

    items: List[Dict[str, Any]] = []
    item_num = 0
    for det in inf_nfe.iter():
        if _local_name(det.tag) != 'det':
            continue
        item_num += 1
        prod = _find_child(det, 'prod')
        if prod is None:
            continue

        x_prod = _get_child_text(prod, 'xProd')
        if not x_prod:
            continue

        q_com = _decimal(_get_child_text(prod, 'qCom'))
        if q_com <= 0:
            q_com = _decimal(_get_child_text(prod, 'qTrib'))
        if q_com <= 0:
            continue

        v_un_com = _decimal(_get_child_text(prod, 'vUnCom'))
        if v_un_com <= 0:
            v_un_com = _decimal(_get_child_text(prod, 'vUnTrib'))
        v_prod = _decimal(_get_child_text(prod, 'vProd'))
        if v_prod <= 0 and v_un_com > 0:
            v_prod = (v_un_com * q_com).quantize(Decimal('0.01'))

        ncm = _get_child_text(prod, 'NCM')
        cfop = _get_child_text(prod, 'CFOP')

        items.append({
            'item_number': item_num,
            'description': x_prod[:500],
            'ncm': ncm[:10] if ncm else '',
            'cfop': cfop[:4] if cfop else '',
            'qty': q_com,
            'unit_price': v_un_com,
            'total': v_prod,
        })

    return {
        'chave': access_key,
        'emitente': emitente or emitente_cnpj or '-',
        'emitente_cnpj': emitente_cnpj,
        'destinatario': destinatario,
        'data_emissao': dh_emi,
        'valor_total': str(v_nf),
        'situacao': '1',
        'items': items,
    }
