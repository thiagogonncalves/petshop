"""
Tasks Celery para importação fiscal (por chave e por NSU).
"""
import logging
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_kwargs={'max_retries': 5},
    soft_time_limit=90,
    time_limit=120,
)
def import_by_key(self, company_id: int, user_id: int, access_key: str):
    """
    Importa NF-e por chave de acesso via SEFAZ NFeDistribuicaoDFe.
    - Carrega config fiscal e certificado
    - Consulta por chNFe
    - Salva resumo e XML quando disponível
    - Cria NFeItem quando XML completo
    """
    from .models import NFeImport, NFeItem, NFeImportStatus, CompanyFiscalConfig
    from .services.crypto import fiscal_crypto
    from .services.sefaz_client import SefazDistribuicaoClient
    from .services.xml_parser import (
        decode_doc_zip,
        parse_res_nfe_xml,
        parse_nfe_xml_fiscal,
    )
    from .validators import validate_access_key
    from apps.users.models import CompanySettings

    key = validate_access_key(access_key)
    company = CompanySettings.objects.filter(pk=company_id).first()
    if not company:
        logger.warning('Company not found', extra={'company_id': company_id})
        return

    config = CompanyFiscalConfig.objects.filter(company=company, is_active=True).first()
    if not config or not config.cert_pfx_encrypted or not config.cert_password_encrypted:
        _mark_error(company_id, access_key, 'Certificado fiscal não configurado.')
        return

    try:
        pfx_data = config.cert_pfx_encrypted
        pfx_bytes = bytes(pfx_data) if pfx_data is not None else b''
        pass_data = config.cert_password_encrypted
        if isinstance(pass_data, str):
            pass_data = pass_data.encode('utf-8')
        elif pass_data is not None:
            pass_data = bytes(pass_data)
        pfx = fiscal_crypto.decrypt(pfx_bytes)
        password = fiscal_crypto.decrypt_str(pass_data or b'')
    except Exception as e:
        logger.warning('Falha ao descriptografar certificado: %s', str(e), exc_info=True)
        _mark_error(company_id, access_key, 'Certificado inválido ou chave de criptografia incorreta. Reenvie o certificado em Configuração SEFAZ.')
        return

    nfe, created = NFeImport.objects.get_or_create(
        company=company,
        access_key=key,
        defaults={
            'status': NFeImportStatus.PENDING,
        },
    )
    if not created and nfe.status == NFeImportStatus.IMPORTED:
        logger.info('NF-e já importada', extra={'access_key': key[:20] + '...'})
        return

    nfe.status = NFeImportStatus.PROCESSING
    nfe.imported_by_id = user_id
    nfe.save(update_fields=['status', 'imported_by', 'updated_at'])

    try:
        client = SefazDistribuicaoClient(
            pfx_bytes=pfx,
            password=password,
            cnpj=config.cnpj,
            uf=config.uf,
            tp_amb=1,
        )
        result = client.distribuicao_por_chave(key)
    except SoftTimeLimitExceeded:
        nfe.status = NFeImportStatus.PENDING
        nfe.sefaz_cstat = 'TIMEOUT'
        nfe.sefaz_xmotivo = 'Timeout na consulta SEFAZ'
        nfe.save(update_fields=['status', 'sefaz_cstat', 'sefaz_xmotivo', 'updated_at'])
        raise
    except Exception as e:
        err_msg = str(e)
        logger.warning('SEFAZ error: %s', err_msg, extra={'access_key': key[:20]})
        nfe.status = NFeImportStatus.ERROR
        nfe.sefaz_xmotivo = str(e)[:500]
        nfe.save(update_fields=['status', 'sefaz_xmotivo', 'updated_at'])
        return

    c_stat = result.get('cStat', '')
    x_motivo = result.get('xMotivo', '')
    nfe.sefaz_cstat = c_stat
    nfe.sefaz_xmotivo = x_motivo
    nfe.nsu = result.get('ultNSU')

    if c_stat != '138' and c_stat != '137':
        nfe.status = NFeImportStatus.ERROR
        nfe.save(update_fields=['status', 'sefaz_cstat', 'sefaz_xmotivo', 'nsu', 'updated_at'])
        return

    doc_zips = result.get('docZip_list', [])
    for doc in doc_zips:
        schema = doc.get('schema', '')
        value = doc.get('value', '')
        if not value:
            continue
        try:
            xml_bytes, detected_schema = decode_doc_zip(value)
            schema = schema or detected_schema
        except Exception as e:
            logger.warning('Erro ao decodificar docZip', extra={'error': str(e)})
            continue

        with transaction.atomic():
            if 'resNFe' in schema or schema == 'resNFe':
                try:
                    resumo = parse_res_nfe_xml(xml_bytes)
                    nfe.resumo_json = resumo
                    nfe.schema = 'resNFe'
                except Exception as e:
                    logger.warning('Erro parse resNFe', extra={'error': str(e)})

            if 'procNFe' in schema or 'nfeProc' in schema or 'NFe' in schema:
                try:
                    parsed = parse_nfe_xml_fiscal(xml_bytes)
                    nfe.resumo_json = {
                        'chave': parsed['chave'],
                        'emitente': parsed['emitente'],
                        'destinatario': parsed['destinatario'],
                        'data_emissao': parsed['data_emissao'],
                        'valor_total': parsed['valor_total'],
                        'situacao': parsed.get('situacao', '1'),
                    }
                    nfe.schema = schema
                    xml_enc = fiscal_crypto.encrypt(xml_bytes)
                    xml_hash = fiscal_crypto.hash_xml(xml_bytes)
                    nfe.xml_encrypted = xml_enc
                    nfe.xml_hash = xml_hash
                    NFeItem.objects.filter(nfe_import=nfe).delete()
                    for item in parsed.get('items', []):
                        NFeItem.objects.create(
                            nfe_import=nfe,
                            item_number=item['item_number'],
                            description=item['description'],
                            ncm=item.get('ncm', ''),
                            cfop=item.get('cfop', ''),
                            qty=item['qty'],
                            unit_price=item['unit_price'],
                            total=item['total'],
                        )
                except Exception as e:
                    logger.warning('Erro parse procNFe', extra={'error': str(e)})

    nfe.status = NFeImportStatus.IMPORTED
    nfe.imported_at = timezone.now()
    nfe.save(update_fields=[
        'status', 'resumo_json', 'schema', 'xml_encrypted', 'xml_hash',
        'sefaz_cstat', 'sefaz_xmotivo', 'nsu', 'imported_at', 'updated_at',
    ])
    logger.info('NF-e importada', extra={'access_key': key[:20], 'has_xml': bool(nfe.xml_encrypted)})


def _mark_error(company_id: int, access_key: str, message: str):
    from .models import NFeImport, NFeImportStatus
    from apps.users.models import CompanySettings

    company = CompanySettings.objects.filter(pk=company_id).first()
    if not company:
        return
    nfe = NFeImport.objects.filter(company=company, access_key=access_key).first()
    if nfe:
        nfe.status = NFeImportStatus.ERROR
        nfe.sefaz_xmotivo = message[:500]
        nfe.save(update_fields=['status', 'sefaz_xmotivo', 'updated_at'])


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_kwargs={'max_retries': 3},
    soft_time_limit=120,
    time_limit=150,
)
def sync_by_nsu(self, company_id: int, user_id=None, max_docs: int = 50):
    """
    Sincroniza NF-es por ultNSU (job diário ou botão "Sincronizar agora").
    """
    from .models import NFeImport, NFeItem, NFeImportStatus, CompanyFiscalConfig
    from .services.crypto import fiscal_crypto
    from .services.sefaz_client import SefazDistribuicaoClient
    from .services.xml_parser import decode_doc_zip, parse_res_nfe_xml, parse_nfe_xml_fiscal
    from apps.users.models import CompanySettings

    company = CompanySettings.objects.filter(pk=company_id).first()
    if not company:
        return

    config = CompanyFiscalConfig.objects.filter(company=company, is_active=True).first()
    if not config or not config.cert_pfx_encrypted or not config.cert_password_encrypted:
        logger.warning('Config fiscal não encontrada', extra={'company_id': company_id})
        return

    try:
        pfx = fiscal_crypto.decrypt(bytes(config.cert_pfx_encrypted))
        password = fiscal_crypto.decrypt_str(bytes(config.cert_password_encrypted))
    except Exception:
        return

    client = SefazDistribuicaoClient(
        pfx_bytes=pfx,
        password=password,
        cnpj=config.cnpj,
        uf=config.uf,
        tp_amb=1,
    )

    last_nsu = config.last_nsu or '0'
    docs_processed = 0

    while docs_processed < max_docs:
        try:
            result = client.distribuicao_por_ult_nsu(last_nsu)
        except Exception as e:
            logger.warning('SEFAZ sync error', extra={'error': str(e)})
            break

        c_stat = result.get('cStat', '')
        new_ult = result.get('ultNSU')
        cons_max = result.get('consMaxNSU')
        doc_zips = result.get('docZip_list', [])

        if new_ult:
            config.last_nsu = new_ult.lstrip('0') or '0'
            config.save(update_fields=['last_nsu', 'updated_at'])

        if c_stat not in ('137', '138', '656'):
            break

        if c_stat == '656':
            break

        for doc in doc_zips:
            if docs_processed >= max_docs:
                break
            value = doc.get('value', '')
            schema = doc.get('schema', '')
            if not value:
                continue
            try:
                xml_bytes, detected_schema = decode_doc_zip(value)
                schema = schema or detected_schema
            except Exception:
                continue

            access_key = None
            if 'resNFe' in schema or schema == 'resNFe':
                try:
                    resumo = parse_res_nfe_xml(xml_bytes)
                    access_key = resumo.get('chave', '')
                except Exception:
                    continue

            if ('procNFe' in schema or 'nfeProc' in schema or 'NFe' in schema) and not access_key:
                try:
                    parsed = parse_nfe_xml_fiscal(xml_bytes)
                    access_key = parsed.get('chave', '')
                except Exception:
                    continue

            if not access_key or len(access_key) != 44:
                continue

            nfe, created = NFeImport.objects.get_or_create(
                company=company,
                access_key=access_key,
                defaults={'status': NFeImportStatus.PENDING},
            )
            if created:
                docs_processed += 1

            with transaction.atomic():
                if 'resNFe' in schema or schema == 'resNFe':
                    try:
                        resumo = parse_res_nfe_xml(xml_bytes)
                        nfe.resumo_json = resumo
                        nfe.schema = 'resNFe'
                        nfe.status = NFeImportStatus.IMPORTED
                        nfe.imported_at = timezone.now()
                        nfe.nsu = result.get('ultNSU')
                        nfe.sefaz_cstat = c_stat
                        nfe.sefaz_xmotivo = result.get('xMotivo', '')
                        nfe.save()
                    except Exception:
                        pass

                if 'procNFe' in schema or 'nfeProc' in schema or 'NFe' in schema:
                    try:
                        parsed = parse_nfe_xml_fiscal(xml_bytes)
                        nfe.resumo_json = {
                            'chave': parsed['chave'],
                            'emitente': parsed['emitente'],
                            'destinatario': parsed['destinatario'],
                            'data_emissao': parsed['data_emissao'],
                            'valor_total': parsed['valor_total'],
                            'situacao': parsed.get('situacao', '1'),
                        }
                        nfe.schema = schema
                        xml_enc = fiscal_crypto.encrypt(xml_bytes)
                        nfe.xml_encrypted = xml_enc
                        nfe.xml_hash = fiscal_crypto.hash_xml(xml_bytes)
                        nfe.status = NFeImportStatus.IMPORTED
                        nfe.imported_at = timezone.now()
                        nfe.nsu = result.get('ultNSU')
                        nfe.sefaz_cstat = c_stat
                        nfe.sefaz_xmotivo = result.get('xMotivo', '')
                        nfe.save()
                        NFeItem.objects.filter(nfe_import=nfe).delete()
                        for item in parsed.get('items', []):
                            NFeItem.objects.create(
                                nfe_import=nfe,
                                item_number=item['item_number'],
                                description=item['description'],
                                ncm=item.get('ncm', ''),
                                cfop=item.get('cfop', ''),
                                qty=item['qty'],
                                unit_price=item['unit_price'],
                                total=item['total'],
                            )
                    except Exception:
                        pass

        if not doc_zips or (new_ult and cons_max and new_ult == cons_max):
            break
        last_nsu = config.last_nsu or new_ult or last_nsu

    logger.info('Sync NSU concluído', extra={'company_id': company_id, 'docs': docs_processed})


@shared_task
def sync_all_companies_by_nsu(max_docs: int = 100):
    """
    Job diário: sincroniza NSU para todas as empresas com config fiscal ativa.
    """
    from .models import CompanyFiscalConfig

    for config in CompanyFiscalConfig.objects.filter(is_active=True).select_related('company'):
        sync_by_nsu.delay(config.company_id, user_id=None, max_docs=max_docs)
