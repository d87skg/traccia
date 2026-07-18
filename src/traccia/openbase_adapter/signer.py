"""
OpenBase Signer Bridge
Bridges Traccia's SHA-256 file signing to OpenBase's Ed25519 per-event signing.
"""

import hashlib
import json
from typing import Optional

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization
    HAS_ED25519 = True
except ImportError:
    HAS_ED25519 = False


class OpenBaseSignerBridge:
    """Signs evidence using OpenBase Ed25519 when available, falls back to SHA-256."""

    def __init__(self):
        if HAS_ED25519:
            self._private_key = ed25519.Ed25519PrivateKey.generate()
            self._public_key = self._private_key.public_key()
            import base64
            raw = self._public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            )
            self.public_key_str = f"ed25519:{base64.b64encode(raw).decode('ascii')}"
        else:
            self._private_key = None
            self.public_key_str = "sha256:fallback"

    def sign_evidence(self, evidence: dict) -> dict:
        """Sign evidence dict and populate hash + signature fields."""
        data = json.dumps(evidence, sort_keys=True, separators=(',', ':')).encode('utf-8')
        evidence["hash"] = hashlib.sha256(data).hexdigest()
        evidence["public_key"] = self.public_key_str

        if HAS_ED25519 and self._private_key:
            message = (evidence["hash"] + evidence["execution_id"]).encode('ascii')
            raw_sig = self._private_key.sign(message)
            import base64
            evidence["signature"] = f"ed25519:{base64.b64encode(raw_sig).decode('ascii')}"
        else:
            evidence["signature"] = f"sha256:{evidence['hash']}"

        return evidence

    def sign_chain(self, evidence_chain: list) -> list:
        """Sign an entire evidence chain."""
        previous_hash = None
        signed_chain = []

        for evidence in evidence_chain:
            evidence["causal"]["parent_id"] = previous_hash
            evidence = self.sign_evidence(evidence)
            previous_hash = evidence["hash"]
            signed_chain.append(evidence)

        return signed_chain

    def verify_chain(self, evidence_chain: list) -> bool:
        """Verify hash chain integrity."""
        for i in range(1, len(evidence_chain)):
            if evidence_chain[i]["causal"]["parent_id"] != evidence_chain[i-1]["hash"]:
                return False
        return True
