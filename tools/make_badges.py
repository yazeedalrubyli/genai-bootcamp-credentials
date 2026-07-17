# -*- coding: utf-8 -*-
"""Render the three tier badge images (circular seals) to PNG via headless Chrome, and write
their Open Badges 3.0 Achievement (BadgeClass) definitions."""
import os, subprocess, json
from lib import REPO_DIR, BASE, DID

# ring/ring2 = outer ring gradient; clight = center accent text (on navy); cstar = star color
TIERS = {
    "distinction": {"label": "DISTINCTION", "ring": "#C7A24A", "ring2": "#E4C878", "ink": "#16304A",
                    "clight": "#E4C878", "cstar": "#E4C878", "stars": 3,
                    "desc": "Top-tier completion: an outstanding, deployed Generative AI project (deliverables score ≥ 60/70)."},
    "merit":       {"label": "MERIT", "ring": "#8A94A6", "ring2": "#B9C1CE", "ink": "#16304A",
                    "clight": "#C7CEDA", "cstar": "#C7CEDA", "stars": 2,
                    "desc": "Strong completion: a solid, deployed Generative AI project (deliverables score ≥ 50/70)."},
    "completion":  {"label": "COMPLETION", "ring": "#9C6B33", "ring2": "#C99A63", "ink": "#16304A",
                    "clight": "#E4C39A", "cstar": "#CFA168", "stars": 1,
                    "desc": "Completed the bootcamp with a passing, deployed Generative AI capstone project."},
}

def svg(t):
    cx = cy = 300; R = 292
    star = lambda x, y, s, c: (
        f'<path transform="translate({x},{y}) scale({s})" fill="{c}" '
        f'd="M0,-10 L2.9,-3.1 L10,-3.1 L4.2,1.6 L6.5,9 L0,4.5 L-6.5,9 L-4.2,1.6 L-10,-3.1 L-2.9,-3.1 Z"/>')
    stars = ""
    n = t["stars"]; sp = 34
    for i in range(n):
        stars += star(cx + (i - (n - 1) / 2) * sp, 398, 1.5, t["cstar"])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="600" height="600">
  <defs>
    <path id="topArc" d="M 92,300 A 208,208 0 0 1 508,300" fill="none"/>
    <path id="botArc" d="M 96,300 A 204,204 0 0 0 504,300" fill="none"/>
    <linearGradient id="ring" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{t['ring2']}"/><stop offset="1" stop-color="{t['ring']}"/>
    </linearGradient>
  </defs>
  <circle cx="{cx}" cy="{cy}" r="{R}" fill="#ffffff"/>
  <circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="url(#ring)" stroke-width="16"/>
  <circle cx="{cx}" cy="{cy}" r="252" fill="none" stroke="{t['ring']}" stroke-width="2.5"/>
  <circle cx="{cx}" cy="{cy}" r="176" fill="{t['ink']}"/>
  <circle cx="{cx}" cy="{cy}" r="176" fill="none" stroke="{t['ring']}" stroke-width="3"/>
  <text font-family="Georgia,serif" font-size="30" font-weight="bold" letter-spacing="3" fill="{t['ink']}">
    <textPath href="#topArc" startOffset="50%" text-anchor="middle">GENERATIVE AI BOOTCAMP</textPath>
  </text>
  <text font-family="Georgia,serif" font-size="23" letter-spacing="3" fill="{t['ink']}">
    <textPath href="#botArc" startOffset="50%" text-anchor="middle">NAJRAN UNIVERSITY &#183; 2026</textPath>
  </text>
  <text x="{cx}" y="248" text-anchor="middle" font-family="Georgia,serif" font-size="30" font-weight="bold" letter-spacing="6" fill="{t['clight']}">AI</text>
  <line x1="228" y1="266" x2="372" y2="266" stroke="{t['ring']}" stroke-width="1.5"/>
  <text x="{cx}" y="322" text-anchor="middle" font-family="Georgia,serif" font-size="{46 if len(t['label'])<8 else 38}" font-weight="bold" letter-spacing="2" fill="#ffffff">{t['label']}</text>
  <text x="{cx}" y="352" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" letter-spacing="1.5" fill="{t['clight']}">AI TEAM</text>
  {stars}
</svg>'''

def main():
    outdir = os.path.join(REPO_DIR, "badges")
    for key, t in TIERS.items():
        html = "<!doctype html><meta charset=utf-8><body style='margin:0'>" + svg(t) + "</body>"
        tmp = f"/tmp/_badge_{key}.html"; open(tmp, "w").write(html)
        png = os.path.join(outdir, f"{key}.png")
        subprocess.run(["google-chrome-stable", "--headless=new", "--disable-gpu", "--no-sandbox",
                        "--hide-scrollbars", "--force-device-scale-factor=2",
                        "--window-size=600,600", f"--screenshot={png}", tmp],
                       capture_output=True, timeout=60)
        # Open Badges 3.0 Achievement (BadgeClass)
        ach = {
            "@context": ["https://www.w3.org/ns/credentials/v2",
                         "https://purl.imsglobal.org/spec/ob/v3p0/context-3.0.3.json"],
            "id": f"{BASE}/badges/{key}.json", "type": ["Achievement"],
            "name": f"Generative AI Summer Bootcamp — {t['label'].title()}",
            "description": t["desc"],
            "creator": DID,
            "criteria": {"id": f"{BASE}/#criteria",
                         "narrative": ("Awarded to participants who completed the 4-week Generative AI Summer "
                                       "Bootcamp (40 training hours) and shipped a working, publicly deployed "
                                       "capstone project, independently assessed against the published rubric.")},
            "image": {"id": f"{BASE}/badges/{key}.png", "type": "Image"},
            "tag": ["Generative AI", "LLM", "RAG", "Multimodal AI", "Hugging Face"],
        }
        json.dump(ach, open(os.path.join(outdir, f"{key}.json"), "w"), ensure_ascii=False, indent=2)
        print(f"  {key}: rendered {os.path.getsize(png)//1024}KB + Achievement json")

if __name__ == "__main__":
    main()
