# Generative AI Summer Bootcamp — Verified Digital Credentials

Self-issued, cryptographically-signed **Open Badges 3.0** credentials for the Najran University
Generative AI Summer Bootcamp (College of CCIS, Year of AI 2026), hosted as a static site on
GitHub Pages. No third-party credentialing platform — so the credentials survive independently of
any vendor.

## Why self-issued
Each credential is a **W3C Verifiable Credential** signed with an **Ed25519** key. Verification
checks the signature against the issuer's public key (published in [`did.json`](did.json)) — not a
live lookup on someone else's server. As long as this GitHub Pages site (or any copy of these files)
is reachable and the public key is available, the badges verify. The trust anchor is the issuer's
key + domain, which you control.

## What's here
| Path | What it is |
|------|-----------|
| `index.html` | Public landing page (no student roster) |
| `did.json` | `did:web` document with the issuer public key |
| `issuer/` | Open Badges 3.0 issuer profile + public JWK |
| `badges/` | The three tier Achievement definitions + seal images |
| `credentials/<id>.json` | Each signed credential (VC + JWS proof) + a baked PNG |
| `v/<id>.html` | Each recipient's verification page (live in-browser signature check) |
| `status/revocation.json` | Revocation list (edit to revoke a credential) |
| `tools/` | The issuance scripts (transparency / re-issuance) |

## Publish (one-time)
1. Create a **public** GitHub repo named `genai-bootcamp-credentials` under `yazeedalrubyli`.
2. Push these files (see below).
3. **Settings → Pages → Deploy from branch → `main` / root.** The site goes live at
   `https://yazeedalrubyli.github.io/genai-bootcamp-credentials/`.
4. Send each student their own verification link (the **private** distribution list is at
   `../badge-issuer-PRIVATE-KEY/distribution-list.csv`, kept outside this repo). Each page has an
   **Add to LinkedIn** button.

> If the repo name or username changes, the credential URLs and the `did:web` change too — pick a
> stable name, or point a custom domain (e.g. a university subdomain via one CNAME record) at Pages
> and re-issue against it. See `tools/lib.py` to change the base URL / DID.

## 🔑 The private signing key — keep it safe
The private key lives **outside this repo** at `../badge-issuer-PRIVATE-KEY/issuer-ed25519.private.jwk`
and must **never** be committed or shared. Anyone with it can forge credentials in your name. Only the
**public** key is published here. Back the private key up somewhere secure.

## Verify a credential
- **In a browser:** open any `v/<id>.html` — it verifies the signature live.
- **From the terminal:** `python tools/verify.py credentials/<id>.json`

## Re-issue / revoke
- Re-issue (new cohort): update the recipients file and run `python tools/issue.py`.
- Revoke: add the credential id to `status/revocation.json` → `revokedCredentials` and push.

---
Issued by the AI Team, College of Computer Science &amp; Information Systems, Najran University.
