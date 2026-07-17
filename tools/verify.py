# -*- coding: utf-8 -*-
"""Standalone verifier: fetch/read the issuer public key and check a credential's EdDSA signature.
Usage: python verify.py ../credentials/<id>.json   (or a raw .jwt string)"""
import json, sys, os
from cryptography.exceptions import InvalidSignature
from lib import REPO_DIR, pub_from_jwk, verify_jws

def main(arg):
    if os.path.isfile(arg):
        obj = json.load(open(arg))
        jws = obj["proof_jwt"] if isinstance(obj, dict) and "proof_jwt" in obj else obj
    else:
        jws = arg
    jwk = json.load(open(os.path.join(REPO_DIR, "issuer", "public-key.jwk.json")))
    pub = pub_from_jwk(jwk)
    try:
        payload = verify_jws(jws, pub)
        subj = payload["credentialSubject"]
        print("✓ SIGNATURE VALID — authentically issued.")
        print("  Recipient:", subj.get("name"))
        print("  Achievement:", subj["achievement"]["name"])
        print("  Issuer:", payload["issuer"]["id"])
        print("  Issued:", payload["validFrom"])
    except InvalidSignature:
        print("✗ SIGNATURE INVALID — tampered or wrong key."); sys.exit(1)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else sys.exit("give a credential path"))
