import os, base64
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from web3 import Web3

def bytes32_keccak(blob: bytes) -> bytes: return Web3.keccak(blob)
def model_bytes(model) -> bytes:
    parts = []
    for p in model.state_dict().values(): parts.append(p.detach().cpu().numpy().tobytes())
    return b"".join(parts)
def model_update_hash(model) -> bytes: return bytes32_keccak(model_bytes(model))

def generate_aes_key() -> bytes: return os.urandom(32)
def encrypt_message(message: bytes, key: bytes) -> str:
    iv = os.urandom(16); cipher = AES.new(key, AES.MODE_CBC, iv)
    pad = 16 - (len(message)%16); ct = cipher.encrypt(message + bytes([pad])*pad)
    return base64.b64encode(iv+ct).decode()
def decrypt_message(ciphertext_b64: str, key: bytes) -> bytes:
    data = base64.b64decode(ciphertext_b64); iv, ct = data[:16], data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv); pt = cipher.decrypt(ct); pad = pt[-1]; return pt[:-pad]

def generate_rsa_keys():
    key = RSA.generate(2048); return key.export_key(), key.publickey().export_key()
def sign_message(private_key_bytes: bytes, message: bytes) -> str:
    key = RSA.import_key(private_key_bytes); h = SHA256.new(message)
    sig = pkcs1_15.new(key).sign(h); return base64.b64encode(sig).decode()
def verify_signature(public_key_bytes: bytes, message: bytes, signature_b64: str) -> bool:
    key = RSA.import_key(public_key_bytes); h = SHA256.new(message)
    try: pkcs1_15.new(key).verify(h, base64.b64decode(signature_b64)); return True
    except Exception: return False
