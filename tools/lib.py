# -*- coding: utf-8 -*-
"""Shared config + Ed25519 / JWS helpers for the self-issued Open Badges 3.0 credentials.
Standard: Open Badges 3.0 (a W3C Verifiable Credentials profile), signed as VC-JWT (EdDSA)."""
import base64, json, os
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

# ---- Identity / hosting config (edit these if you change username / repo / domain) ----
USERNAME = "yazeedalrubyli"
REPO     = "genai-bootcamp-credentials"
BASE     = f"https://{USERNAME}.github.io/{REPO}"
DID      = f"did:web:{USERNAME}.github.io:{REPO}"   # resolves to <BASE>/did.json
KID      = DID + "#key-1"

ISSUER_NAME = "Generative AI Summer Bootcamp — AI Team, Najran University"
ISSUER_URL  = "https://www.nu.edu.sa"

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY_PATH = os.path.abspath(os.path.join(REPO_DIR, "..", "badge-issuer-PRIVATE-KEY", "issuer-ed25519.private.jwk"))

def b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

def b64u_dec(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))

def public_jwk(pub: Ed25519PublicKey) -> dict:
    raw = pub.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return {"kty": "OKP", "crv": "Ed25519", "x": b64u(raw)}

def load_private() -> Ed25519PrivateKey:
    jwk = json.load(open(KEY_PATH))
    raw = b64u_dec(jwk["d"])
    return Ed25519PrivateKey.from_private_bytes(raw)

def pub_from_jwk(jwk: dict) -> Ed25519PublicKey:
    return Ed25519PublicKey.from_public_bytes(b64u_dec(jwk["x"]))

def sign_jws(payload: dict, priv: Ed25519PrivateKey, kid: str = KID) -> str:
    header = {"alg": "EdDSA", "typ": "JWT", "kid": kid}
    h = b64u(json.dumps(header, separators=(",", ":")).encode())
    p = b64u(json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode())
    sig = priv.sign(f"{h}.{p}".encode())
    return f"{h}.{p}.{b64u(sig)}"

def verify_jws(jws: str, pub: Ed25519PublicKey) -> dict:
    h, p, s = jws.split(".")
    pub.verify(b64u_dec(s), f"{h}.{p}".encode())   # raises on tamper/invalid
    return json.loads(b64u_dec(p))
