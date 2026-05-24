import random
class IdentityVault:
    def __init__(self):
        self.synthetic_identities = {}
        self.virtual_tpms = {}

    def generate_synthetic_identity(self, persona_type: str):
        print(f"[IdentityVault] Generating Quantum-Resistant Synthetic Identity for persona: {persona_type}")
        identity = {"name": f"{persona_type}_John_{random.randint(100,999)}", "email": f"j.{random.randint(1000,9999)}@proxy.net"}
        self.synthetic_identities[identity["email"]] = identity
        return identity

    def inject_virtual_tpm(self, domain: str):
        print(f"[IdentityVault] Injecting virtual TPM for Passkey/WebAuthn bypass on {domain}")
        self.virtual_tpms[domain] = True