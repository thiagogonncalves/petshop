"""
Views do módulo fiscal - config e NF-e.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from apps.users.models import CompanySettings
from apps.users.permissions import IsAdmin

from .models import CompanyFiscalConfig, NFeImport
from .serializers import (
    CompanyFiscalConfigSerializer,
    CompanyFiscalConfigCreateUpdateSerializer,
    NFeImportListSerializer,
    NFeImportDetailSerializer,
)
from .tasks import import_by_key, sync_by_nsu
from .validators import validate_access_key
from .services.crypto import fiscal_crypto


def _get_company(request):
    """Retorna a empresa atual (singleton)."""
    return CompanySettings.objects.first()


class FiscalConfigView(APIView):
    """
    GET /api/fiscal/config/ - retorna configuração fiscal
    POST /api/fiscal/config/ - cria/atualiza (multipart: pfx_file, pfx_password, cnpj, uf)
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        company = _get_company(request)
        if not company:
            return Response({'detail': 'Empresa não configurada.'}, status=status.HTTP_404_NOT_FOUND)
        config = CompanyFiscalConfig.objects.filter(company=company).first()
        if not config:
            return Response(None)
        serializer = CompanyFiscalConfigSerializer(config)
        return Response(serializer.data)

    def post(self, request):
        if not IsAdmin().has_permission(request, self):
            return Response(
                {'detail': 'Somente administradores podem configurar o certificado fiscal.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        company = _get_company(request)
        if not company:
            return Response({'detail': 'Empresa não configurada.'}, status=status.HTTP_404_NOT_FOUND)

        pfx_file = request.FILES.get('pfx_file') or request.FILES.get('pfx')
        pfx_password = request.data.get('pfx_password') or request.POST.get('pfx_password')
        cnpj = ''.join(filter(str.isdigit, str(request.data.get('cnpj') or request.POST.get('cnpj') or '')))
        uf = (request.data.get('uf') or request.POST.get('uf') or '').upper()[:2]

        if not pfx_file:
            return Response(
                {'error': 'Envie o arquivo PFX (pfx_file).'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not pfx_password:
            return Response(
                {'error': 'Informe a senha do certificado (pfx_password).'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(cnpj) != 14:
            return Response(
                {'error': 'CNPJ deve ter 14 dígitos.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(uf) != 2:
            return Response(
                {'error': 'UF deve ter 2 caracteres.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cnpj = ''.join(filter(str.isdigit, cnpj))
        pfx_bytes = pfx_file.read()

        try:
            cert_enc = fiscal_crypto.encrypt(pfx_bytes)
            pass_enc = fiscal_crypto.encrypt_str(pfx_password)
            # TextField precisa de string; Fernet retorna bytes em base64 (ASCII)
            pass_enc_str = pass_enc.decode('utf-8') if isinstance(pass_enc, bytes) else str(pass_enc)
        except Exception as e:
            return Response(
                {'error': 'Erro ao criptografar. Verifique DJANGO_FISCAL_ENCRYPTION_KEY.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        config, _ = CompanyFiscalConfig.objects.update_or_create(
            company=company,
            defaults={
                'cnpj': cnpj,
                'uf': uf,
                'cert_pfx_encrypted': cert_enc,
                'cert_password_encrypted': pass_enc_str,
                'is_active': True,
            },
        )
        serializer = CompanyFiscalConfigSerializer(config)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NFeImportByKeyView(APIView):
    """
    POST /api/fiscal/nfe/import-by-key/
    Body: { "access_key": "44 dígitos" }
    Cria NFeImport PENDING e dispara task Celery.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request):
        company = _get_company(request)
        if not company:
            return Response({'detail': 'Empresa não configurada.'}, status=status.HTTP_404_NOT_FOUND)

        access_key = (request.data.get('access_key') or '').strip()
        try:
            key = validate_access_key(access_key)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        config = CompanyFiscalConfig.objects.filter(company=company, is_active=True).first()
        if not config:
            return Response(
                {'error': 'Configure o certificado fiscal antes de importar NF-e.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        nfe, created = NFeImport.objects.get_or_create(
            company=company,
            access_key=key,
            defaults={'status': 'pending'},
        )
        if not created and nfe.status == 'imported':
            serializer = NFeImportDetailSerializer(nfe)
            return Response(
                {'message': 'NF-e já importada.', 'nfe': serializer.data},
                status=status.HTTP_200_OK,
            )

        if not created:
            nfe.status = 'pending'
            nfe.save(update_fields=['status', 'updated_at'])

        import_by_key.delay(company.id, request.user.id, key)
        nfe.refresh_from_db()
        serializer = NFeImportDetailSerializer(nfe)
        if nfe.status == 'error':
            return Response(
                {
                    'error': nfe.sefaz_xmotivo or 'Erro ao consultar SEFAZ.',
                    'nfe': serializer.data,
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(
            {'message': 'Importação em andamento.' if nfe.status == 'processing' else 'NF-e importada.', 'nfe': serializer.data},
            status=status.HTTP_202_ACCEPTED,
        )


class NFeSyncView(APIView):
    """POST /api/fiscal/nfe/sync/ - dispara sync_by_nsu."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        company = _get_company(request)
        if not company:
            return Response({'detail': 'Empresa não configurada.'}, status=status.HTTP_404_NOT_FOUND)

        config = CompanyFiscalConfig.objects.filter(company=company, is_active=True).first()
        if not config:
            return Response(
                {'error': 'Configure o certificado fiscal antes de sincronizar.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        sync_by_nsu.delay(company.id, request.user.id)
        return Response(
            {'message': 'Sincronização iniciada em segundo plano.'},
            status=status.HTTP_202_ACCEPTED,
        )


class NFeImportViewSet(ReadOnlyModelViewSet):
    """GET /api/fiscal/nfe/ - lista | GET /api/fiscal/nfe/{id}/ - detalhe."""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        company = _get_company(self.request)
        if not company:
            return NFeImport.objects.none()
        qs = NFeImport.objects.filter(company=company)
        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)
        tem_xml = self.request.query_params.get('tem_xml')
        if tem_xml is not None and str(tem_xml).lower() in ('true', '1', 'yes'):
            qs = qs.exclude(xml_encrypted__isnull=True).exclude(xml_encrypted=b'')
        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return NFeImportDetailSerializer
        return NFeImportListSerializer

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['access_key']
    ordering_fields = ['created_at', 'imported_at']
    ordering = ['-created_at']


class NFeXmlDownloadView(APIView):
    """GET /api/fiscal/nfe/{id}/xml/ - download do XML (somente admin)."""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        if not IsAdmin().has_permission(request, self):
            return Response(
                {'detail': 'Somente administradores podem baixar o XML.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        company = _get_company(request)
        if not company:
            return Response({'detail': 'Empresa não configurada.'}, status=status.HTTP_404_NOT_FOUND)

        nfe = get_object_or_404(NFeImport, pk=pk, company=company)
        if not nfe.xml_encrypted:
            return Response(
                {'detail': 'XML não disponível para esta NF-e.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            xml_bytes = fiscal_crypto.decrypt(bytes(nfe.xml_encrypted))
        except Exception:
            return Response(
                {'detail': 'Erro ao descriptografar XML.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        resp = HttpResponse(xml_bytes, content_type='application/xml')
        resp['Content-Disposition'] = f'attachment; filename="nfe_{nfe.access_key}.xml"'
        return resp
