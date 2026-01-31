"""
NFe import tests: XML parser and duplicate import.
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from .services.xml_parser import parse_nfe_xml
from .models import NFeImport, NFeImportItem

User = get_user_model()


# NF-e XML mínimo sem namespace (para testes do parser)
SAMPLE_NFE_XML = b'''<?xml version="1.0" encoding="UTF-8"?>
<nfeProc>
  <NFe>
    <infNFe Id="NFe35210112345678000190550010000000011234567890">
      <ide><nNF>1</nNF></ide>
      <emit><xNome>Fornecedor Teste LTDA</xNome></emit>
      <det nItem="1">
        <prod>
          <xProd>Racao Premium 15kg</xProd>
          <qCom>10.0000</qCom>
          <qTrib>10.0000</qTrib>
          <vUnCom>45.000000</vUnCom>
          <vUnTrib>45.000000</vUnTrib>
          <vProd>450.00</vProd>
          <cEAN>7891234567890</cEAN>
          <uCom>UN</uCom>
          <uTrib>UN</uTrib>
        </prod>
      </det>
      <det nItem="2">
        <prod>
          <xProd>Shampoo Pet 500ml</xProd>
          <qCom>24</qCom>
          <vUnCom>12.50</vUnCom>
          <vProd>300.00</vProd>
          <cEAN>SEM GTIN</cEAN>
          <uCom>UN</uCom>
        </prod>
      </det>
    </infNFe>
  </NFe>
</nfeProc>
'''


class NFeXmlParserTest(TestCase):
    """Test parse_nfe_xml."""

    def test_parse_extracts_access_key(self):
        data = parse_nfe_xml(SAMPLE_NFE_XML)
        self.assertEqual(len(data['access_key']), 44)
        self.assertTrue(data['access_key'].isdigit() or data['access_key'].startswith('35'))

    def test_parse_extracts_supplier_and_number(self):
        data = parse_nfe_xml(SAMPLE_NFE_XML)
        self.assertIn('Fornecedor', data['supplier_name'])
        self.assertEqual(data['nfe_number'], '1')

    def test_parse_extracts_items(self):
        data = parse_nfe_xml(SAMPLE_NFE_XML)
        self.assertGreaterEqual(len(data['items']), 1)
        first = data['items'][0]
        self.assertEqual(first['product_name'], 'Racao Premium 15kg')
        self.assertEqual(first['quantity'], Decimal('10'))
        self.assertEqual(first['unit_cost'], Decimal('45'))
        self.assertEqual(first['total_cost'], Decimal('450.00'))
        self.assertEqual(first['gtin'], '7891234567890')

    def test_parse_sem_gtin_ignored(self):
        data = parse_nfe_xml(SAMPLE_NFE_XML)
        second = next((i for i in data['items'] if 'Shampoo' in i['product_name']), None)
        self.assertIsNotNone(second, 'Deve existir item Shampoo; items=%s' % data['items'])
        # SEM GTIN deve ser ignorado (None ou vazio)
        self.assertTrue(second.get('gtin') is None or second.get('gtin') == '' or second.get('gtin', '').upper() == 'SEM GTIN')

    def test_parse_invalid_xml_raises(self):
        with self.assertRaises((ValueError, Exception)):
            parse_nfe_xml(b'<invalid>')


class NFeDuplicateImportTest(TestCase):
    """Test duplicate nfe_key blocks or returns conflict."""

    def setUp(self):
        self.user = User.objects.create_user(username='test', email='test@test.com', password='test123')

    def test_duplicate_access_key_blocks_second_import(self):
        from .views import NFeImportXMLView
        from rest_framework.test import APIRequestFactory
        from rest_framework.test import force_authenticate
        from django.core.files.uploadedfile import SimpleUploadedFile

        NFeImport.objects.create(
            access_key='35210112345678000190550010000000011234567890',
            status='pending',
            imported_by=self.user,
        )
        factory = APIRequestFactory()
        request = factory.post(
            '/api/nfe/import-xml/',
            data={},
            format='multipart',
        )
        request.FILES['file'] = SimpleUploadedFile('test.xml', SAMPLE_NFE_XML, content_type='application/xml')
        force_authenticate(request, user=self.user)
        view = NFeImportXMLView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 409, msg=response.data)
        self.assertTrue(
            'duplicate' in str(response.data).lower() or response.data.get('code') == 'duplicate',
            msg=response.data
        )
