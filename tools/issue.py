# -*- coding: utf-8 -*-
"""Issue signed Open Badges 3.0 credentials (VC-JWT / EdDSA) to the certified recipients:
writes public credential JSON + verification page per recipient, a baked badge PNG, the
revocation status list, and a PRIVATE distribution list (kept outside the repo)."""
import json, os, hashlib, secrets, html as H, urllib.parse, datetime, shutil
from PIL import Image, PngImagePlugin
from lib import (REPO_DIR, BASE, DID, KID, ISSUER_NAME, ISSUER_URL, load_private,
                 sign_jws, b64u)

RECIPIENTS = "/home/y/Desktop/GenAI Bootcamp/Grading/reports/badge_recipients.json"
PRIVATE_OUT = os.path.abspath(os.path.join(REPO_DIR, "..", "badge-issuer-PRIVATE-KEY", "distribution-list.csv"))
NOW = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
YEAR, MONTH = 2026, 7

TIER_KEY = {"Distinction": "distinction", "Merit": "merit", "Completion": "completion"}
TIER_DESC = {
    "Distinction": "with Distinction",
    "Merit": "with Merit",
    "Completion": "",
}

def credential(cid, name, tier, email, evidence):
    tkey = TIER_KEY[tier]
    salt = secrets.token_hex(8)
    ihash = "sha256$" + hashlib.sha256((email + salt).encode()).hexdigest()
    ach = json.load(open(os.path.join(REPO_DIR, "badges", f"{tkey}.json")))
    subject = {
        "type": ["AchievementSubject"],
        "name": name,
        "identifier": [{"type": "IdentityObject", "identityType": "emailAddress",
                        "hashed": True, "salt": salt, "identityHash": ihash}],
        "achievement": ach,
    }
    vc = {
        "@context": ["https://www.w3.org/ns/credentials/v2",
                     "https://purl.imsglobal.org/spec/ob/v3p0/context-3.0.3.json"],
        "id": f"{BASE}/credentials/{cid}.json",
        "type": ["VerifiableCredential", "OpenBadgeCredential"],
        "name": f"Generative AI Summer Bootcamp — {tier}",
        "issuer": {"id": DID, "type": ["Profile"], "name": ISSUER_NAME, "url": ISSUER_URL},
        "validFrom": NOW,
        "credentialSubject": subject,
        "credentialStatus": {"id": f"{BASE}/status/revocation.json#{cid}",
                             "type": "1EdTechRevocationList"},
    }
    if evidence:
        vc["evidence"] = [{"id": evidence, "type": ["Evidence"],
                           "name": "Deployed capstone / project",
                           "description": "The recipient's own publicly deployed Generative AI project."}]
    return vc, tkey

def bake_png(tkey, cid, jws):
    src = os.path.join(REPO_DIR, "badges", f"{tkey}.png")
    im = Image.open(src)
    meta = PngImagePlugin.PngInfo()
    meta.add_itxt("openbadgecredential", jws)          # baked assertion (JWS)
    meta.add_text("verify", f"{BASE}/v/{cid}")
    out = os.path.join(REPO_DIR, "credentials", f"{cid}.png")
    im.save(out, pnginfo=meta)

def linkedin_url(cid, tier):
    q = {"startTask": "CERTIFICATION_NAME",
         "name": f"Generative AI Summer Bootcamp — {tier}",
         "organizationName": "Najran University",
         "issueYear": YEAR, "issueMonth": MONTH,
         "certUrl": f"{BASE}/v/{cid}", "certId": cid}
    return "https://www.linkedin.com/profile/add?" + urllib.parse.urlencode(q)

def verify_page(cid, name, tier, evidence, jws, li_url, arabic=None):
    tkey = TIER_KEY[tier]
    tier_line = f"Generative AI Summer Bootcamp <b>— {tier}</b>"
    ev = (f'<a href="{H.escape(evidence)}" target="_blank" rel="noopener">View the recipient\'s deployed project ↗</a>'
          if evidence else "—")
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{H.escape(name)} — Generative AI Bootcamp ({tier}) — Verified Credential</title>
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<link rel="icon" href="../favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="../apple-touch-icon.png">
<style>
:root{{--navy:#16304a;--gold:#c7a24a;--ink:#1b2836;--muted:#5b6875;--line:#e5e9ee;--bg:#f5f6f8}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);
font-family:-apple-system,Segoe UI,Roboto,"Noto Sans Arabic",sans-serif;line-height:1.55}}
.card{{max-width:640px;margin:32px auto;background:#fff;border:1px solid var(--line);border-radius:16px;
box-shadow:0 6px 30px rgba(20,40,70,.07);overflow:hidden}}
.top{{background:var(--navy);color:#fff;padding:22px 28px;font-size:12px;letter-spacing:.12em;text-transform:uppercase}}
.top b{{color:var(--gold)}}
.body{{padding:8px 28px 26px;text-align:center}}
.badge{{width:200px;height:200px;margin:14px auto 6px;display:block}}
h1{{font-family:Georgia,serif;font-size:24px;color:var(--navy);margin:8px 0 2px}}
.tier{{font-family:Georgia,serif;font-size:15px;color:var(--muted);margin:0 0 14px}}
.who{{font-size:15px;color:var(--muted)}}.who b{{color:var(--ink)}}
.meta{{text-align:left;border-top:1px solid var(--line);margin-top:18px;padding-top:14px;font-size:14px}}
.row{{display:flex;justify-content:space-between;gap:14px;padding:6px 0;border-bottom:1px solid var(--line)}}
.row:last-child{{border-bottom:none}} .row span{{color:var(--muted)}} .row b{{color:var(--ink);text-align:right}}
.verify{{margin-top:16px;padding:12px 14px;border-radius:10px;font-size:13.5px;background:#f0f4f9;color:var(--navy)}}
.verify.ok{{background:#eaf6ee;color:#1f7a43}} .verify.bad{{background:#fbecec;color:#b3352b}}
.btn{{display:inline-block;margin:16px 6px 4px;padding:11px 18px;border-radius:9px;font-weight:600;font-size:14px;text-decoration:none}}
.li{{background:#0a66c2;color:#fff}} .ghost{{background:#fff;color:var(--navy);border:1px solid var(--line)}}
details{{margin-top:12px;text-align:left;font-size:12.5px;color:var(--muted)}}
summary{{cursor:pointer;color:var(--navy);font-weight:600}}
code{{word-break:break-all;background:#f4f6f8;display:block;padding:8px;border-radius:6px;margin-top:6px;font-size:11px}}
.foot{{text-align:center;color:var(--muted);font-size:11.5px;padding:14px}}
</style></head><body>
<div class="card">
  <div class="top">Verified Digital Credential · <b>Open Badges 3.0</b></div>
  <div class="body">
    <img class="badge" src="../badges/{tkey}.png?v=aiteam" alt="{tier} badge">
    <h1>{tier_line}</h1>
    <p class="who">Awarded to <b>{H.escape(name)}</b></p>
    <div id="vbox" class="verify">⏳ Verifying the issuer's digital signature…</div>
    <div class="meta">
      <div class="row"><span>Program</span><b>Generative AI Summer Bootcamp (40 hours)</b></div>
      <div class="row"><span>Issuer</span><b>AI Team, Najran University</b></div>
      <div class="row"><span>Issued</span><b>{NOW[:10]}</b></div>
      <div class="row"><span>Evidence</span><b>{ev}</b></div>
      <div class="row"><span>Credential ID</span><b>{cid}</b></div>
    </div>
    <a class="btn li" href="{H.escape(li_url)}" target="_blank" rel="noopener">Add to LinkedIn</a>
    <a class="btn ghost" href="../credentials/{cid}.json" target="_blank" rel="noopener">Credential JSON</a>
    <details><summary>How to verify this yourself</summary>
      This credential is a W3C Verifiable Credential (Open Badges 3.0) signed with the issuer's
      Ed25519 key. Verification below is computed live in your browser: it fetches the issuer's public
      key from <a href="../did.json" target="_blank">did.json</a> and checks the signature (EdDSA) over
      the credential. Nothing here depends on a third-party platform.
      <code id="jws">{jws}</code>
    </details>
  </div>
</div>
<div class="foot">Issued by the AI Team, Najran University</div>
<script>
const JWS="{jws}";
function b64u(s){{s=s.replace(/-/g,'+').replace(/_/g,'/');while(s.length%4)s+='=';const b=atob(s);const u=new Uint8Array(b.length);for(let i=0;i<b.length;i++)u[i]=b.charCodeAt(i);return u;}}
(async()=>{{
  const box=document.getElementById('vbox');
  try{{
    const [h,p,s]=JWS.split('.');
    const did=await (await fetch('../did.json',{{cache:'no-store'}})).json();
    const jwk=did.verificationMethod[0].publicKeyJwk;
    const key=await crypto.subtle.importKey('jwk',{{kty:'OKP',crv:'Ed25519',x:jwk.x}},{{name:'Ed25519'}},false,['verify']);
    const data=new TextEncoder().encode(h+'.'+p);
    const ok=await crypto.subtle.verify({{name:'Ed25519'}},key,b64u(s),data);
    if(ok){{box.className='verify ok';box.innerHTML='✓ Signature valid — authentically issued by Najran University · AI Team.';}}
    else{{box.className='verify bad';box.innerHTML='✗ Signature INVALID — this credential may have been altered.';}}
  }}catch(e){{
    box.className='verify';box.innerHTML='ℹ️ Signature could not be auto-checked in this browser (needs Ed25519 WebCrypto support). The credential JSON and issuer key are linked above for manual verification.';
  }}
}})();
</script>
</body></html>'''

def main():
    recips = json.load(open(RECIPIENTS))
    priv = load_private()
    vdir = os.path.join(REPO_DIR, "v"); cdir = os.path.join(REPO_DIR, "credentials")
    for d in (vdir, cdir):
        os.makedirs(d, exist_ok=True)
    dist = ["student_id,name,tier,verification_url,linkedin_add_url,email"]
    status_ids = []
    for r in recips:
        cid = secrets.token_hex(8)
        vc, tkey = credential(cid, r["name"], r["tier"], r["email"], r.get("evidence"))
        jws = sign_jws(vc, priv)
        # public files
        json.dump({"credential": vc, "proof_jwt": jws},
                  open(os.path.join(cdir, f"{cid}.json"), "w"), ensure_ascii=False, indent=2)
        li = linkedin_url(cid, r["tier"])
        open(os.path.join(vdir, f"{cid}.html"), "w").write(
            verify_page(cid, r["name"], r["tier"], r.get("evidence"), jws, li))
        bake_png(tkey, cid, jws)
        status_ids.append(cid)
        vurl = f"{BASE}/v/{cid}"
        dist.append(f'{r["id"]},"{r["name"]}",{r["tier"]},{vurl},{li},{r["email"]}')
    # revocation status list (empty = none revoked)
    json.dump({"@context": ["https://www.w3.org/ns/credentials/v2"],
               "id": f"{BASE}/status/revocation.json", "type": ["1EdTechRevocationList"],
               "issuer": DID, "revokedCredentials": []},
              open(os.path.join(REPO_DIR, "status", "revocation.json"), "w"), indent=2)
    # PRIVATE distribution list (outside repo — do NOT publish)
    open(PRIVATE_OUT, "w").write("\n".join(dist))
    print(f"Issued {len(recips)} signed credentials.")
    print("Public: credentials/*.json, v/*.html, credentials/*.png (baked), status/revocation.json")
    print("PRIVATE distribution list (send each student their own link):", PRIVATE_OUT)

if __name__ == "__main__":
    main()
