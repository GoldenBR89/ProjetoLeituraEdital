import base64
import json
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

class EncryptionManager:
    def __init__(self):
        self.salt = b'static_salt_value_for_kdf'  # Em produção, use um salt aleatório por usuário
    
    def derive_key(self, password: str) -> bytes:
        """Deriva uma chave de criptografia a partir de uma senha"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt_data(self, data: dict, password: str) -> str:
        """Criptografa dados usando a senha do usuário"""
        key = self.derive_key(password)
        cipher_suite = Fernet(key)
        json_data = json.dumps(data).encode()
        encrypted_data = cipher_suite.encrypt(json_data)
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data: str, password: str) -> dict:
        """Descriptografa dados usando a senha do usuário"""
        try:
            key = self.derive_key(password)
            cipher_suite = Fernet(key)
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = cipher_suite.decrypt(decoded_data)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            raise ValueError(f"Falha ao descriptografar dados: {str(e)}")