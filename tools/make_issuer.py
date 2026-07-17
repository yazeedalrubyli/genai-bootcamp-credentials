# -*- coding: utf-8 -*-
"""Generate the issuer Ed25519 key (private key saved OUTSIDE the repo), and write the public
did:web document + Open Badges 3.0 issuer Profile into the repo. Run once."""
import json, os
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from lib import (REPO_DIR, KEY_PATH, DID, KID, ISSUER_NAME, ISSUER_URL,
                 public_jwk, b64u, b64u_dec)

def main():
    if os.path.exists(KEY_PATH):
        print("Private key already exists at", KEY_PATH, "— reusing (delete to regenerate).")
        priv = Ed25519PrivateKey.from_private_bytes(b64u_dec(json.load(open(KEY_PATH))["d"]))
    else:
        priv = Ed25519PrivateKey.generate()
        raw = priv.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
                                 serialization.NoEncryption())
        os.makedirs(os.path.dirname(KEY_PATH), exist_ok=True)
        json.dump({"kty": "OKP", "crv": "Ed25519", "d": b64u(raw),
                   "x": public_jwk(priv.public_key())["x"]},
                  open(KEY_PATH, "w"))
        os.chmod(KEY_PATH, 0o600)
        print("NEW private key written (KEEP SAFE, never commit):", KEY_PATH)

    pub = priv.public_key()
    jwk = public_jwk(pub)

    # did:web document (W3C DID)
    did_doc = {
        "@context": ["https://www.w3.org/ns/did/v1",
                     "https://w3id.org/security/suites/jws-2020/v1"],
        "id": DID,
        "verificationMethod": [{
            "id": KID, "type": "JsonWebKey2020", "controller": DID, "publicKeyJwk": jwk,
        }],
        "assertionMethod": [KID], "authentication": [KID],
    }
    json.dump(did_doc, open(os.path.join(REPO_DIR, "did.json"), "w"), indent=2)

    # Open Badges 3.0 issuer Profile
    issuer = {
        "@context": ["https://www.w3.org/ns/credentials/v2",
                     "https://purl.imsglobal.org/spec/ob/v3p0/context-3.0.3.json"],
        "id": DID, "type": ["Profile"], "name": ISSUER_NAME, "url": ISSUER_URL,
        "description": ("Official issuer profile for the Generative AI Summer Bootcamp run by the "
                        "AI Team of the College of Computer Science & Information Systems, Najran University."),
    }
    os.makedirs(os.path.join(REPO_DIR, "issuer"), exist_ok=True)
    json.dump(issuer, open(os.path.join(REPO_DIR, "issuer", "profile.json"), "w"),
              ensure_ascii=False, indent=2)
    json.dump(jwk, open(os.path.join(REPO_DIR, "issuer", "public-key.jwk.json"), "w"), indent=2)
    print("Wrote did.json, issuer/profile.json, issuer/public-key.jwk.json")
    print("DID:", DID)

if __name__ == "__main__":
    main()
