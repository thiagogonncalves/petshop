"""
NFe Import views: upload XML, import by access key, confirm entry (Purchase + StockMovement).
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db import transaction
from django.conf import settings
from django.shortcuts import get_object_or_404
from decimal import Decimal

from .models import NFeImport, NFeImportItem
from .services.xml_parser import parse_nfe_xml
from .services.fetch_by_key import fetch_nfe_xml_by_key, normalize_access_key
from .serializers import NFeImportSerializer, NFeImportItemSerializer
from apps.products.models import Product, Category, StockMovement, Purchase, PurchaseItem


class NFeImportViewSet(ReadOnlyModelViewSet):
    """List and retrieve NFe imports."""
    queryset = NFeImport.objects.all()
    serializer_class = NFeImportSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status']
    search_fields = ['access_key', 'supplier_name', 'nfe_number']


class NFeImportXMLView(APIView):
    """
    POST /api/nfe/import-xml/
    multipart/form-data: file (XML)
    Returns parsed items; creates NFeImport + NFeImportItem if key not duplicate.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        xml_file = request.FILES.get('file') or request.FILES.get('xml')
        if not xml_file:
            return Response(
                {'error': 'Envie o arquivo XML (campo "file" ou "xml")'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            content = xml_file.read()
            if isinstance(content, str):
                content = content.encode('utf-8')
            data = parse_nfe_xml(content)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': f'Erro ao processar XML: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        access_key = data['access_key']
        if NFeImport.objects.filter(access_key=access_key).exists():
            return Response(
                {
                    'error': 'Esta NF-e já foi importada.',
                    'access_key': access_key,
                    'code': 'duplicate'
                },
                status=status.HTTP_409_CONFLICT
            )

        with transaction.atomic():
            nfe_import = NFeImport.objects.create(
                access_key=access_key,
                supplier_name=data.get('supplier_name', ''),
                nfe_number=data.get('nfe_number', ''),
                status='pending',
                imported_by=request.user
            )
            for item in data['items']:
                NFeImportItem.objects.create(
                    nfe_import=nfe_import,
                    product_name=item['product_name'],
                    quantity=item['quantity'],
                    unit=item.get('unit', 'UN'),
                    unit_cost=item['unit_cost'],
                    total_cost=item['total_cost'],
                    gtin=item.get('gtin'),
                )

        serializer = NFeImportSerializer(nfe_import)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


def _create_nfe_import_from_parsed(request, data):
    """Cria NFeImport + itens a partir do dict retornado por parse_nfe_xml (evita duplicar lógica)."""
    access_key = data['access_key']
    if NFeImport.objects.filter(access_key=access_key).exists():
        return None, {'error': 'Esta NF-e já foi importada.', 'access_key': access_key, 'code': 'duplicate'}, 409
    with transaction.atomic():
        nfe_import = NFeImport.objects.create(
            access_key=access_key,
            supplier_name=data.get('supplier_name', ''),
            nfe_number=data.get('nfe_number', ''),
            status='pending',
            imported_by=request.user
        )
        for item in data['items']:
            NFeImportItem.objects.create(
                nfe_import=nfe_import,
                product_name=item['product_name'],
                quantity=item['quantity'],
                unit=item.get('unit', 'UN'),
                unit_cost=item['unit_cost'],
                total_cost=item['total_cost'],
                gtin=item.get('gtin'),
            )
    return nfe_import, None, None


class NFeImportByKeyView(APIView):
    """
    POST /api/nfe/import-by-key/
    Body: { "access_key": "44 dígitos" }
    Busca o XML pela chave (NFE_FETCH_XML_URL_TEMPLATE) e importa como no upload.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request):
        access_key = (request.data.get('access_key') or '').strip()
        key = normalize_access_key(access_key)
        if not key:
            return Response(
                {'error': 'Informe a chave de acesso da NF-e com 44 dígitos.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        url_template = getattr(settings, 'NFE_FETCH_XML_URL_TEMPLATE', '') or ''
        if not url_template or '{access_key}' not in url_template:
            return Response(
                {
                    'error': 'Importação por chave não está configurada. Use o upload do arquivo XML ou configure NFE_FETCH_XML_URL_TEMPLATE no servidor.'
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            xml_content = fetch_nfe_xml_by_key(key, url_template)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = parse_nfe_xml(xml_content)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': f'Erro ao processar XML: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        nfe_import, err, err_code = _create_nfe_import_from_parsed(request, data)
        if err is not None:
            return Response(err, status=err_code)

        serializer = NFeImportSerializer(nfe_import)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class NFeConfirmView(APIView):
    """
    POST /api/nfe/{import_id}/confirm/
    Body: { "items": [ { "id": <NFeImportItem.id>, "product_id": <Product.id>, "profit_margin": 30 } ] }
    Creates Purchase, PurchaseItem, StockMovement (ENTRADA), updates product cost_price and sale_price.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, import_id):
        nfe_import = get_object_or_404(NFeImport, id=import_id)
        if nfe_import.status != 'pending':
            return Response(
                {'error': 'Importação já foi confirmada ou cancelada.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        items_payload = request.data.get('items')
        if items_payload is None:
            return Response(
                {'error': 'Envie o corpo da requisição com "items": lista de { "id", "product_id" (ou null para criar novo), "profit_margin" (opcional) }.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not isinstance(items_payload, list) or len(items_payload) == 0:
            return Response(
                {'error': 'A lista "items" não pode estar vazia. Cada item deve ter "id" (do item da NF-e), "product_id" (número ou null para criar novo produto) e opcionalmente "profit_margin".'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Build map: nfe_item_id -> { product_id, profit_margin }
        item_map = {int(it.get('id')): it for it in items_payload if it.get('id') is not None}
        nfe_items = list(nfe_import.items.select_related('product').all())
        if not nfe_items:
            return Response({'error': 'Nenhum item na importação.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate: every item must have product_id (create or link)
        default_category = Category.objects.first()
        if not default_category:
            return Response(
                {'error': 'Cadastre ao menos uma categoria de produtos antes de confirmar.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            purchase = Purchase.objects.create(
                supplier_name=nfe_import.supplier_name or 'Fornecedor NF-e',
                nfe_key=nfe_import.access_key,
                nfe_number=nfe_import.nfe_number or '',
                total_value=Decimal('0.00'),
                created_by=request.user
            )
            total_purchase = Decimal('0.00')

            for nfe_item in nfe_items:
                cfg = item_map.get(nfe_item.id, {})
                product_id = cfg.get('product_id')
                profit_margin = Decimal(str(cfg.get('profit_margin', 0)))

                if product_id:
                    product = Product.objects.get(id=product_id)
                else:
                    # Create new product from NFe item
                    product = Product.objects.create(
                        name=nfe_item.product_name[:200],
                        category=default_category,
                        cost_price=nfe_item.unit_cost,
                        profit_margin=profit_margin,
                        price_manually_set=False,
                        unit=nfe_item.unit or 'UN',
                        gtin=nfe_item.gtin or None,
                        stock_quantity=0,
                        min_stock=0,
                    )
                    product.recalculate_sale_price()
                    product.save()

                qty_int = int(nfe_item.quantity)
                if qty_int < 1:
                    continue

                previous_stock = product.stock_quantity
                new_stock = previous_stock + qty_int

                # Update product cost and recalc sale if not manually set
                product.cost_price = nfe_item.unit_cost
                if not product.price_manually_set:
                    product.profit_margin = profit_margin
                    product.recalculate_sale_price()
                product.stock_quantity = new_stock
                product.save(update_fields=['cost_price', 'profit_margin', 'sale_price', 'stock_quantity'])

                # PurchaseItem
                total_cost = nfe_item.quantity * nfe_item.unit_cost
                PurchaseItem.objects.create(
                    purchase=purchase,
                    product=product,
                    quantity=nfe_item.quantity,
                    unit_cost=nfe_item.unit_cost,
                    total_cost=total_cost
                )
                total_purchase += total_cost

                # StockMovement ENTRADA
                StockMovement.objects.create(
                    product=product,
                    movement_type='entry',
                    quantity=qty_int,
                    cost_price=nfe_item.unit_cost,
                    reference=nfe_import.access_key,
                    previous_stock=previous_stock,
                    new_stock=new_stock,
                    created_by=request.user
                )

                nfe_item.product = product
                nfe_item.save(update_fields=['product'])

            purchase.total_value = total_purchase
            purchase.save(update_fields=['total_value'])

            nfe_import.status = 'confirmed'
            nfe_import.save(update_fields=['status'])

        serializer = NFeImportSerializer(nfe_import)
        return Response(serializer.data)
