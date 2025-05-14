import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

class CryptoUtils:
    @staticmethod
    def generate_rsa_keypair():
        key = RSA.generate(2048)
        private_key = key.export_key()
        public_key = key.publickey().export_key()
        return private_key, public_key

    @staticmethod
    def encrypt_with_rsa(public_key, data):
        rsa_key = RSA.import_key(public_key)
        cipher = PKCS1_OAEP.new(rsa_key)
        return cipher.encrypt(data)

    @staticmethod
    def decrypt_with_rsa(private_key, encrypted_data):
        rsa_key = RSA.import_key(private_key)
        cipher = PKCS1_OAEP.new(rsa_key)
        return cipher.decrypt(encrypted_data)

    @staticmethod
    def generate_aes_key():
        return get_random_bytes(32)  # AES-256

    @staticmethod
    def encrypt_with_aes(key, data):
        iv = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(pad(data, AES.block_size))
        return iv + encrypted

    @staticmethod
    def decrypt_with_aes(key, encrypted_data):
        iv = encrypted_data[:16]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(encrypted_data[16:]), AES.block_size)
        return decrypted