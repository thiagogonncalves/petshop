"""
Cliente SOAP para NFeDistribuicaoDFe (Distribuição DF-e).
Usa zeep + requests com certificado A1 (PFX) para TLS.
"""
import json
import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# Zeep opcional - só importa quando usado
try:
    from zeep import Client
    from zeep.transports import Transport
    ZEEP_AVAILABLE = True
except ImportError:
    ZEEP_AVAILABLE = False
    Client = None
    Transport = None

ENDPOINTS_PATH = Path(__file__).resolve().parent.parent / 'data' / 'sefaz_endpoints.json'
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 5
RETRY_BACKOFF = 2  # segundos base


def _load_endpoints() -> Dict:
    """Carrega endpoints por UF do JSON."""
    if not ENDPOINTS_PATH.exists():
        return {}
    with open(ENDPOINTS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def _get_url_for_uf(uf: str, tp_amb: int = 1) -> str:
    """
    Retorna URL do NFeDistribuicaoDFe para a UF.
    tp_amb: 1=produção, 2=homologação
    """
    data = _load_endpoints()
    env = 'production' if tp_amb == 1 else 'homologation'
    urls = data.get(env, {})
    uf = (uf or '').upper()[:2]

    # Verificar se UF usa SVRS
    svrs = data.get('uf_to_svrs', [])
    svan = data.get('uf_to_svan', [])
    lookup_uf = uf
    if uf in svrs:
        lookup_uf = 'SVRS'
    elif uf in svan:
        lookup_uf = 'SVAN'

    return urls.get(lookup_uf) or urls.get('AN') or urls.get('SVRS') or (
        'https://www1.nfe.fazenda.gov.br/NFeDistribuicaoDFe/NFeDistribuicaoDFe.asmx'
        if tp_amb == 1
        else 'https://hom1.nfe.fazenda.gov.br/NFeDistribuicaoDFe/NFeDistribuicaoDFe.asmx'
    )


def _extract_pem_from_pfx(pfx_bytes: bytes, password: str) -> tuple[str, str]:
    """
    Extrai cert e key em PEM do PFX.
    Retorna (cert_pem, key_pem).
    """
    import warnings
    try:
        from cryptography.hazmat.primitives.serialization import pkcs12
        from cryptography.hazmat.backends import default_backend
    except ImportError:
        raise RuntimeError('Instale cryptography: pip install cryptography')

    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', message='PKCS#12 bundle could not be parsed as DER')
        key, cert, _ = pkcs12.load_key_and_certificates(
            pfx_bytes,
            password.encode('utf-8') if isinstance(password, str) else password,
            default_backend()
        )

    from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption

    cert_pem = cert.public_bytes(Encoding.PEM)
    key_pem = key.private_bytes(
        Encoding.PEM,
        PrivateFormat.TraditionalOpenSSL,
        NoEncryption()
    )
    return cert_pem.decode('utf-8'), key_pem.decode('utf-8')


class SefazDistribuicaoClient:
    """
    Cliente para consulta NFeDistribuicaoDFe.
    Suporta consulta por chNFe e por ultNSU.
    """

    def __init__(
        self,
        pfx_bytes: bytes,
        password: str,
        cnpj: str,
        uf: str,
        tp_amb: int = 1,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        if not ZEEP_AVAILABLE:
            raise RuntimeError('Instale zeep: pip install zeep')
        self.cnpj = ''.join(filter(str.isdigit, str(cnpj)))[:14]
        self.uf = (uf or '')[:2].upper()
        self.tp_amb = tp_amb
        self.timeout = timeout

        cert_pem, key_pem = _extract_pem_from_pfx(pfx_bytes, password)
        self._cert_pem = cert_pem
        self._key_pem = key_pem
        self._session = requests.Session()
        self._session.cert = None  # será configurado via arquivos temp
        self._session.verify = True

    def _request(self, body: str, soap_action: str) -> str:
        """Envia requisição SOAP com certificado."""
        url = _get_url_for_uf(self.uf, self.tp_amb)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as cert_f:
            cert_f.write(self._cert_pem)
            cert_f.write('\n')
            cert_f.write(self._key_pem)
            cert_file = cert_f.name
        try:
            self._session.cert = cert_file
            # SEFAZ usa SOAP 1.1 (não SOAP 1.2)
            headers = {
                'Content-Type': 'text/xml; charset=utf-8',
                'SOAPAction': '"nfeDistDFeInteresse"',
            }
            envelope = f'''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:dfe="http://www.portalfiscal.inf.br/nfe/wsdl/NFeDistribuicaoDFe">
  <soap:Body>
    {body}
  </soap:Body>
</soap:Envelope>'''
            resp = self._session.post(url, data=envelope.encode('utf-8'), headers=headers, timeout=self.timeout)
            resp.raise_for_status()
            return resp.text
        finally:
            try:
                os.unlink(cert_file)
            except OSError:
                pass

    def _build_dist_nsu(self, ult_nsu: str) -> str:
        """Monta distNSU para consulta por NSU."""
        return f'''<dfe:nfeDadosMsg>
  <distDFeInt xmlns="http://www.portalfiscal.inf.br/nfe" versao="1.01">
    <tpAmb>{self.tp_amb}</tpAmb>
    <cUFAutor>{self._uf_code()}</cUFAutor>
    <CNPJ>{self.cnpj}</CNPJ>
    <distNSU><ultNSU>{ult_nsu.zfill(15)}</ultNSU></distNSU>
  </distDFeInt>
</dfe:nfeDadosMsg>'''

    def _build_cons_ch_nfe(self, ch_nfe: str) -> str:
        """Monta consNSU/chNFe para consulta por chave."""
        return f'''<dfe:nfeDadosMsg>
  <distDFeInt xmlns="http://www.portalfiscal.inf.br/nfe" versao="1.01">
    <tpAmb>{self.tp_amb}</tpAmb>
    <cUFAutor>{self._uf_code()}</cUFAutor>
    <CNPJ>{self.cnpj}</CNPJ>
    <consChNFe>{ch_nfe}</consChNFe>
  </distDFeInt>
</dfe:nfeDadosMsg>'''

    def _uf_code(self) -> int:
        """Código numérico da UF para cUFAutor."""
        codes = {
            'AC': 12, 'AL': 27, 'AM': 13, 'AP': 16, 'BA': 29, 'CE': 23, 'DF': 53,
            'ES': 32, 'GO': 52, 'MA': 21, 'MG': 31, 'MS': 50, 'MT': 51, 'PA': 15,
            'PB': 25, 'PE': 26, 'PI': 22, 'PR': 41, 'RJ': 33, 'RN': 24, 'RO': 11,
            'RR': 14, 'RS': 43, 'SC': 42, 'SE': 28, 'SP': 35, 'TO': 17,
        }
        return codes.get(self.uf, 35)

    def distribuicao_por_chave(self, ch_nfe: str) -> Dict[str, Any]:
        """
        Consulta NF-e por chave de acesso.
        Retorna dict com: cStat, xMotivo, ultNSU, docZip_list (lista de {schema, value}).
        """
        start = time.time()
        body = self._build_cons_ch_nfe(ch_nfe)
        try:
            xml_resp = self._request(body, 'http://www.portalfiscal.inf.br/nfe/wsdl/NFeDistribuicaoDFe/nfeDistDFeInteresse')
        except requests.RequestException as e:
            elapsed = time.time() - start
            detail = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    detail = f'{e.response.status_code}: {e.response.text[:200]}' if e.response.text else str(e)
                except Exception:
                    pass
            logger.warning('SEFAZ request failed: %s', detail)
            raise RuntimeError(f'SEFAZ indisponível: {detail[:200]}') from e

        elapsed = time.time() - start
        return self._parse_response(xml_resp, elapsed_ms=round(elapsed * 1000))

    def distribuicao_por_ult_nsu(self, ult_nsu: str) -> Dict[str, Any]:
        """
        Consulta por último NSU conhecido.
        Retorna dict com: cStat, xMotivo, ultNSU, consMaxNSU, docZip_list.
        """
        start = time.time()
        body = self._build_dist_nsu(ult_nsu)
        try:
            xml_resp = self._request(body, 'http://www.portalfiscal.inf.br/nfe/wsdl/NFeDistribuicaoDFe/nfeDistDFeInteresse')
        except requests.RequestException as e:
            elapsed = time.time() - start
            detail = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    detail = f'{e.response.status_code}: {e.response.text[:200]}' if e.response.text else str(e)
                except Exception:
                    pass
            logger.warning('SEFAZ request failed (NSU): %s', detail)
            raise RuntimeError(f'SEFAZ indisponível: {detail[:200]}') from e

        elapsed = time.time() - start
        return self._parse_response(xml_resp, elapsed_ms=round(elapsed * 1000))

    def _parse_response(self, xml_resp: str, elapsed_ms: int = 0) -> Dict[str, Any]:
        """Parse da resposta SOAP retornando cStat, xMotivo, docZip_list."""
        import xml.etree.ElementTree as ET

        ns = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'soap12': 'http://www.w3.org/2003/05/soap-envelope',
            'dfe': 'http://www.portalfiscal.inf.br/nfe',
        }
        root = ET.fromstring(xml_resp)
        body = (
            root.find('.//soap:Body', ns)
            or root.find('.//{http://schemas.xmlsoap.org/soap/envelope/}Body')
            or root.find('.//{http://www.w3.org/2003/05/soap-envelope}Body')
        )
        if body is None:
            for el in root.iter():
                if 'Body' in (el.tag or ''):
                    body = el
                    break
        if body is None:
            raise ValueError('Resposta SOAP inválida: Body não encontrado')

        def find_any(parent, local_name):
            for c in parent.iter():
                tag = c.tag or ''
                if '}' in tag:
                    tag = tag.split('}', 1)[1]
                if tag == local_name:
                    return c
            return None

        ret = root
        for wrapper in ['nfeDistDFeInteresseResult', 'retDistDFeInt', 'loteDistDFeInt']:
            r = find_any(body if body is not None else root, wrapper)
            if r is not None:
                ret = r
                break

        c_stat = None
        x_motivo = None
        ult_nsu = None
        cons_max_nsu = None
        doc_zips = []

        for el in ret.iter():
            tag = el.tag or ''
            if '}' in tag:
                tag = tag.split('}', 1)[1]
            if tag == 'cStat':
                c_stat = (el.text or '').strip()
            elif tag == 'xMotivo':
                x_motivo = (el.text or '').strip()
            elif tag == 'ultNSU':
                ult_nsu = (el.text or '').strip()
            elif tag == 'consMaxNSU':
                cons_max_nsu = (el.text or '').strip()
            elif tag == 'docZip':
                schema = el.get('schema') or ''
                doc_zips.append({'schema': schema, 'value': (el.text or '').strip()})

        result = {
            'cStat': c_stat or '',
            'xMotivo': x_motivo or '',
            'ultNSU': ult_nsu,
            'consMaxNSU': cons_max_nsu,
            'docZip_list': doc_zips,
            'elapsed_ms': elapsed_ms,
        }
        logger.info('SEFAZ response', extra={
            'cStat': result['cStat'],
            'doc_count': len(doc_zips),
            'elapsed_ms': elapsed_ms,
        })
        return result
