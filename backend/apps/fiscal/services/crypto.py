"""
Criptografia simétrica para certificado, senha e XML fiscal.
Usa Fernet (AES) com chave em DJANGO_FISCAL_ENCRYPTION_KEY.
Nunca logar senha ou conteúdo do PFX.
"""
import base64
import hashlib
import logging
import os

from django.conf import settings

logger = logging.getLogger(__name__)

try:
    from cryptography.fernet import Fernet, InvalidToken
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError:
    Fernet = None
    InvalidToken = Exception  # fallback


def _get_fernet():
    """Obtém instância Fernet a partir da chave em variável de ambiente."""
    if Fernet is None:
        raise RuntimeError(
            'Instale cryptography: pip install cryptography'
        )
    key = os.environ.get('DJANGO_FISCAL_ENCRYPTION_KEY') or getattr(
        settings, 'FISCAL_ENCRYPTION_KEY', ''
    )
    if not key:
        raise RuntimeError(
            'Configure DJANGO_FISCAL_ENCRYPTION_KEY (32 bytes base64) ou '
            'gere com: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
        )
    if isinstance(key, str):
        key = key.encode('utf-8')
    return Fernet(key)


def _derive_key_from_secret(secret: str) -> bytes:
    """Deriva chave Fernet a partir de uma string (fallback)."""
    if Fernet is None:
        raise RuntimeError('Instale cryptography')
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'petshop_fiscal_v1',
        iterations=480000,
    )
    derived = base64.urlsafe_b64encode(kdf.derive(secret.encode('utf-8')))
    return derived


class FiscalCrypto:
    """Criptografia para dados fiscais sensíveis."""

    def __init__(self):
        self._fernet = None

    def _get_fernet_safe(self):
        if self._fernet is None:
            try:
                self._fernet = _get_fernet()
            except Exception:
                secret = getattr(settings, 'SECRET_KEY', 'fallback-secret')
                key = _derive_key_from_secret(secret)
                self._fernet = Fernet(key)
        return self._fernet

    def encrypt(self, plain: bytes) -> bytes:
        """Criptografa bytes. Retorna bytes base64."""
        if not plain:
            return b''
        f = self._get_fernet_safe()
        return f.encrypt(plain)

    def decrypt(self, encrypted: bytes) -> bytes:
        """Descriptografa. Levanta InvalidToken se chave inválida."""
        if not encrypted:
            return b''
        f = self._get_fernet_safe()
        return f.decrypt(encrypted)

    def encrypt_str(self, plain: str) -> bytes:
        """Criptografa string -> bytes."""
        return self.encrypt(plain.encode('utf-8'))

    def decrypt_str(self, encrypted: bytes) -> str:
        """Descriptografa -> string."""
        return self.decrypt(encrypted).decode('utf-8')

    @staticmethod
    def hash_xml(xml_content: bytes) -> str:
        """Calcula SHA256 do XML (integridade). Nunca logar o conteúdo."""
        return hashlib.sha256(xml_content).hexdigest()


fiscal_crypto = FiscalCrypto()
