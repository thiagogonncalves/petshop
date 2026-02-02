"""
Busca XML da NF-e pela chave de acesso.
Configurável via NFE_FETCH_XML_URL_TEMPLATE (ex: https://api.exemplo.com/nfe/{access_key}/xml).
"""
import re
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


def normalize_access_key(key: str) -> str:
    """Remove espaços e mantém só dígitos; retorna string vazia se inválida."""
    if not key or not isinstance(key, str):
        return ''
    digits = re.sub(r'\D', '', key.strip())
    return digits if len(digits) == 44 else ''


def fetch_nfe_xml_by_key(access_key: str, url_template: str) -> bytes:
    """
    Obtém o XML da NF-e pela chave usando a URL configurada.
    url_template: string com placeholder {access_key}, ex: "https://api.com/nfe/{access_key}/xml"
    Retorna bytes do XML.
    Levanta ValueError se url_template vazio, chave inválida ou falha na requisição.
    """
    key = normalize_access_key(access_key)
    if not key:
        raise ValueError('Chave de acesso deve ter exatamente 44 dígitos.')

    if not url_template or '{access_key}' not in url_template:
        raise ValueError(
            'Importação por chave não configurada. '
            'Configure NFE_FETCH_XML_URL_TEMPLATE no ambiente ou use o upload de XML.'
        )

    url = url_template.format(access_key=key)
    try:
        req = Request(url, headers={'User-Agent': 'GB-PET/1.0'})
        with urlopen(req, timeout=30) as resp:
            content = resp.read()
    except HTTPError as e:
        raise ValueError(f'Não foi possível obter a NF-e (HTTP {e.code}). Verifique a chave e o provedor.')
    except URLError as e:
        raise ValueError(f'Erro ao acessar o serviço de NF-e: {e.reason}')
    except Exception as e:
        raise ValueError(f'Erro ao buscar XML: {str(e)}')

    if not content or len(content) < 100:
        raise ValueError('Resposta do serviço não contém um XML válido.')

    return content
