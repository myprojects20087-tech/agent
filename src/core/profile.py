import json

class UserProfile:
    def __init__(self, name: str, preferences: dict):
        self.name = name
        self.preferences = preferences

    @classmethod
    def load(cls, filepath: str) -> "UserProfile":
        print(f"[UserProfile] Loading profile from {filepath}")
        return cls(name="DefaultUser", preferences={"stealth_level": "high"})

    def get_credentials(self, domain: str) -> dict:
        print(f"[UserProfile] Fetching secure credentials for {domain}")
        return {"username": "admin", "token": "encrypted_vault_key"}