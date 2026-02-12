"""
Testes do módulo fiscal.
"""
import base64
import gzip
from unittest.mock import patch, MagicMock
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from apps.users.models import CompanySettings
from .validators import normalize_access_key, validate_access_key
from .services.crypto import FiscalCrypto
from .services.xml_parser import parse_res_nfe_xml, decode_doc_zip

User = get_user_model()


class TestAccessKeyValidation(TestCase):
    def test_normalize_valid(self):
        self.assertEqual(
            normalize_access_key('35210112345678000190550010000000011234567890'),
            '35210112345678000190550010000000011234567890',
        )
        self.assertEqual(
            normalize_access_key('3521 0112 3456 7800 0190 5500 1000 0000 0112 3456 7890'),
            '35210112345678000190550010000000011234567890',
        )

    def test_normalize_invalid(self):
        self.assertEqual(normalize_access_key('123'), '')
        self.assertEqual(normalize_access_key(''), '')
        self.assertEqual(normalize_access_key('352101123456780001905500100000000112345678901'), '')

    def test_validate_raises(self):
        with self.assertRaises(ValueError):
            validate_access_key('123')
        with self.assertRaises(ValueError):
            validate_access_key('')


class TestCrypto(TestCase):
    def setUp(self):
        self.crypto = FiscalCrypto()

    def test_hash_xml(self):
        h = FiscalCrypto.hash_xml(b'<nfe>test</nfe>')
        self.assertEqual(len(h), 64)
        self.assertTrue(all(c in '0123456789abcdef' for c in h))

    def test_encrypt_decrypt_roundtrip(self):
        plain = b'secret data'
        enc = self.crypto.encrypt(plain)
        self.assertNotEqual(enc, plain)
        dec = self.crypto.decrypt(enc)
        self.assertEqual(dec, plain)


class TestXmlParser(TestCase):
    def test_parse_res_nfe_minimal(self):
        xml = '''<?xml version="1.0"?>
        <resNFe xmlns="http://www.portalfiscal.inf.br/nfe">
            <chNFe>35210112345678000190550010000000011234567890</chNFe>
            <xNome>EMPRESA TESTE</xNome>
            <dhEmi>2021-01-15T10:00:00-03:00</dhEmi>
            <vNF>100.00</vNF>
            <cSitNFe>1</cSitNFe>
        </resNFe>'''
        data = parse_res_nfe_xml(xml.encode('utf-8'))
        self.assertEqual(data['chave'], '35210112345678000190550010000000011234567890')
        self.assertIn('EMPRE', data['emitente'])
        self.assertEqual(data['valor_total'], '100.00')


class TestDecodeDocZip(TestCase):
    def test_decode_doczip(self):
        xml = b'<resNFe xmlns="http://www.portalfiscal.inf.br/nfe"><chNFe>123</chNFe></resNFe>'
        compressed = gzip.compress(xml)
        encoded = base64.b64encode(compressed).decode('ascii')
        out_xml, schema = decode_doc_zip(encoded)
        self.assertEqual(out_xml, xml)
        self.assertIn('resNFe', schema)
