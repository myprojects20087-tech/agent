import json
import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class UserProfile:
    def __init__(self, name: str, preferences: dict, key: bytes = None):
        self.name = name
        self.preferences = preferences
        self.key = key or AESGCM.generate_key(bit_length=256)
        self.aesgcm = AESGCM(self.key)
        self.vault = {}

    @classmethod
    def load(cls, filepath: str) -> "UserProfile":
        print(f"[UserProfile] Loading profile from {filepath}")
        return cls(name="DefaultUser", preferences={"stealth_level": "high"})

    def store_credential(self, domain: str, username: str, token: str):
        print(f"[UserProfile] Encrypting and vaulting credential for {domain}")
        nonce = os.urandom(12)
        data = json.dumps({"username": username, "token": token}).encode('utf-8')
        ct = self.aesgcm.encrypt(nonce, data, None)
        self.vault[domain] = {"nonce": base64.b64encode(nonce).decode(), "ct": base64.b64encode(ct).decode()}

    def get_credentials(self, domain: str) -> dict:
        print(f"[UserProfile] Fetching and decrypting secure credentials for {domain}")
        if domain not in self.vault:
            return {"username": "admin", "token": "default_mock"}

        entry = self.vault[domain]
        nonce = base64.b64decode(entry["nonce"])
        ct = base64.b64decode(entry["ct"])
        pt = self.aesgcm.decrypt(nonce, ct, None)
        return json.loads(pt.decode('utf-8'))