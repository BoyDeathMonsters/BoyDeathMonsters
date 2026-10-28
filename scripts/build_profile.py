#!/usr/bin/env python3
"""Génère les cartes SVG du profil GitHub (style néon turquoise).

Lancé chaque nuit par .github/workflows/profile.yml.
Usage local :  python3 scripts/build_profile.py --mock   (données factices)
"""
import base64
import datetime as dt
import json
import math
import os
import sys
import urllib.request
from html import escape

# ───────────────────────── CONFIG ─────────────────────────
LOGIN = os.environ.get("PROFILE_LOGIN") or os.environ.get("GITHUB_REPOSITORY_OWNER") or "BoyDeathMonsters"
DISPLAY_NAME = "Florent BAJARD"
TAGLINE = "👋 Hi, I'm Florent Bajard   🎓 Engineering Student @ ICAM Toulouse"
SOCIALS = [  # (icône, label, valeur affichée)
    ("G", "GitHub", "@boydeathmonsters"),
    ("in", "LinkedIn", "florent-bajard"),
    ("IG", "Instagram", "@flobajard4"),
    ("@", "Email", "florent.bajard"),
]
MAX_PROJECTS = 6
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

# ───────────────────────── THEME ─────────────────────────
W = 900
MINT = "#7ef0d8"
MINT_SOFT = "#5fd3bd"
TEXT = "#e9fffa"
MUTED = "#8cc7bb"
SANS = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"
DISPLAY = "'Segoe UI Black', 'Arial Black', 'Segoe UI', Ubuntu, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"


def text_w(s, size, k=0.58):
    return len(s) * size * k


def card(h, body, extra_defs="", extra_css=""):
    """Carte extérieure dégradée + panneau intérieur en verre."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#0f3b37"/>
    <stop offset=".45" stop-color="#0a2524"/>
    <stop offset="1" stop-color="#0b1d2b"/>
  </linearGradient>
  <radialGradient id="glowA" cx=".18" cy="0" r=".55">
    <stop offset="0" stop-color="#2fb7a2" stop-opacity=".75"/>
    <stop offset="1" stop-color="#2fb7a2" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="glowB" cx=".9" cy="1" r=".55">
    <stop offset="0" stop-color="#5468c9" stop-opacity=".6"/>
    <stop offset="1" stop-color="#5468c9" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="glowC" cx=".55" cy=".35" r=".45">
    <stop offset="0" stop-color="#1f8f80" stop-opacity=".35"/>
    <stop offset="1" stop-color="#1f8f80" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#7ef0d8" stop-opacity=".9"/>
    <stop offset=".5" stop-color="#2dd4bf" stop-opacity=".35"/>
    <stop offset="1" stop-color="#7c8cf0" stop-opacity=".7"/>
  </linearGradient>
  <linearGradient id="panel" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#052224" stop-opacity=".55"/>
    <stop offset="1" stop-color="#061418" stop-opacity=".66"/>
  </linearGradient>
  {extra_defs}
</defs>
<style>
  text{{font-family:{SANS}}}
  .mono{{font-family:{MONO}}}
  {extra_css}
</style>
<rect x="1" y="1" width="{W-2}" height="{h-2}" rx="24" fill="url(#bg)"/>
<rect x="1" y="1" width="{W-2}" height="{h-2}" rx="24" fill="url(#glowA)"/>
<rect x="1" y="1" width="{W-2}" height="{h-2}" rx="24" fill="url(#glowB)"/>
<rect x="1" y="1" width="{W-2}" height="{h-2}" rx="24" fill="url(#glowC)"/>
<rect x="1" y="1" width="{W-2}" height="{h-2}" rx="24" fill="none" stroke="url(#edge)" stroke-width="1.5"/>
<rect x="26" y="26" width="{W-52}" height="{h-52}" rx="18" fill="url(#panel)" stroke="#7ef0d8" stroke-opacity=".32"/>
{body}
</svg>"""


# ───────────────────────── DATA ─────────────────────────
QUERY = """
query($login:String!){
  user(login:$login){
    name login avatarUrl followers{totalCount}
    contributionsCollection{ contributionCalendar{ totalContributions
      weeks{ contributionDays{ date contributionCount } } } }
    repositories(first:100, ownerAffiliations:OWNER, privacy:PUBLIC, isFork:false,
                 orderBy:{field:PUSHED_AT, direction:DESC}){
      totalCount
      nodes{ name description url stargazerCount pushedAt isArchived
        primaryLanguage{ name color }
        languages(first:8, orderBy:{field:SIZE, direction:DESC}){
          totalSize edges{ size node{ name color } } } }
    }
  }
}"""


def fetch():
    token = os.environ["GITHUB_TOKEN"]
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    data = json.load(urllib.request.urlopen(req, timeout=60))
    if "errors" in data:
        sys.exit(f"GraphQL error: {data['errors']}")
    u = data["data"]["user"]
    avatar = None
    try:
        sep = "&" if "?" in u["avatarUrl"] else "?"
        raw = urllib.request.urlopen(u["avatarUrl"] + sep + "s=200", timeout=30).read()
        avatar = "data:image/png;base64," + base64.b64encode(raw).decode()
    except Exception as e:  # l'avatar est optionnel
        print("avatar:", e)
    days = [d for w in u["contributionsCollection"]["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    repos = []
    for r in u["repositories"]["nodes"]:
        langs = [(e["node"]["name"], e["node"]["color"] or "#8b949e", e["size"]) for e in r["languages"]["edges"]]
        repos.append({
            "name": r["name"], "description": r["description"], "stars": r["stargazerCount"],
            "pushed": r["pushedAt"], "archived": r["isArchived"], "langs": langs,
        })
    return {
        "login": u["login"], "avatar": avatar, "followers": u["followers"]["totalCount"],
        "repo_count": u["repositories"]["totalCount"],
        "total": u["contributionsCollection"]["contributionCalendar"]["totalContributions"],
        "days": [(d["date"], d["contributionCount"]) for d in days], "repos": repos,
    }


def mock():
    import random
    random.seed(4)
    start = dt.date.today() - dt.timedelta(days=364)
    start -= dt.timedelta(days=(start.weekday() + 1) % 7)
    days = []
    for i in range((dt.date.today() - start).days + 1):
        c = 0
        if 180 < i < 230 and random.random() < .35:
            c = random.choice([1, 2, 4, 9, 18, 30])
        days.append(((start + dt.timedelta(days=i)).isoformat(), c))
    return {
        "login": LOGIN, "avatar": None, "followers": 0, "repo_count": 3, "total": sum(c for _, c in days),
        "days": days,
        "repos": [
            {"name": "firefighter-robot-lancelot", "description": "A field-intervention robotic platform designed to assist firefighters in hazardous environments.",
             "stars": 0, "pushed": "2026-10-20T10:00:00Z", "archived": False,
             "langs": [("Python", "#3572A5", 70), ("C++", "#f34b7d", 22), ("CMake", "#DA3434", 5), ("Shell", "#89e051", 3)]},
            {"name": "Test-Codex", "description": "Test fonction Codex", "stars": 0, "pushed": "2026-09-02T10:00:00Z",
             "archived": False, "langs": [("TypeScript", "#3178c6", 99), ("HTML", "#e34c26", 1)]},
            {"name": "BoyDeathMonsters", "description": None, "stars": 1, "pushed": "2026-10-28T10:00:00Z",
             "archived": False, "langs": [("Python", "#3572A5", 100)]},
        ],
    }


# ───────────────────────── HELPERS ─────────────────────────
def ago(iso):
    if not iso:
        return "n/a"
    d = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))).days
    if d <= 0:
        return "today"
    if d < 30:
        return f"{d}d ago"
    if d < 365:
        return f"{d // 30}mo ago"
    return f"{d // 365}y ago"


def wrap(s, width, lines=2):
    words, out, cur = (s or "").split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) <= width:
            cur = f"{cur} {w}".strip()
        else:
            out.append(cur)
            cur = w
            if len(out) == lines:
                break
    if len(out) < lines and cur:
        out.append(cur)
    if len(out) == lines and " ".join(out) != " ".join(words):
        out[-1] = out[-1][: width - 1].rstrip() + "…"
    return out


def pill(x, y, label, h=28):
    w = text_w(label, 13, .62) + 34
    return (f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{h/2}" fill="#0a2a2a" fill-opacity=".85" '
            f'stroke="#7ef0d8" stroke-opacity=".55"/>'
            f'<text x="{x+17:.1f}" y="{y+h/2+4.5}" font-size="13" font-weight="700" fill="{TEXT}">{escape(label)}</text>'), w


# ───────────────────────── CARDS ─────────────────────────
def header(d, langs, stars):
    h = 260
    if d["avatar"]:
        av = (f'<clipPath id="av"><circle cx="118" cy="110" r="50"/></clipPath>'
              f'<image href="{d["avatar"]}" x="68" y="60" width="100" height="100" clip-path="url(#av)" preserveAspectRatio="xMidYMid slice"/>')
    else:
        av = f'<circle cx="118" cy="110" r="50" fill="#123c3a"/><text x="118" y="124" text-anchor="middle" font-size="40" font-weight="800" fill="{MINT}">{escape(DISPLAY_NAME[:1])}</text>'
    body = f"""
<g class="fade">
  <circle cx="118" cy="110" r="57" fill="none" stroke="#7ef0d8" stroke-opacity=".25" stroke-width="6"/>
  {av}
  <circle cx="118" cy="110" r="51" fill="none" stroke="#7ef0d8" stroke-width="2.5"/>
  <text x="196" y="72" class="mono" font-size="14" font-weight="700" letter-spacing="3" fill="{MINT}">@{escape(d['login'].lower())}</text>
  <path d="M196 84 Q 330 58 470 86" fill="none" stroke="#7ef0d8" stroke-opacity=".45" stroke-width="1.5"/>
  <text x="194" y="132" font-family="{DISPLAY}" font-size="48" font-weight="900" fill="{TEXT}">{escape(DISPLAY_NAME)}</text>
  <text x="196" y="164" font-size="15.5" fill="{MINT}">{escape(TAGLINE)}</text>
</g>
<g class="fade" style="animation-delay:.15s">
  <circle cx="790" cy="110" r="46" fill="#0a2a2a" fill-opacity=".5" stroke="#7ef0d8" stroke-opacity=".18"/>
  <text x="790" y="122" text-anchor="middle" font-size="40" font-weight="800" fill="{MINT}">{stars}</text>
  <text x="790" y="152" text-anchor="middle" font-size="11" font-weight="800" letter-spacing="3" fill="{MINT}">TOTAL STARS</text>
</g>"""
    x, pills = 60, ""
    for l in langs[:4]:
        p, w = pill(x, 190, l)
        pills += p
        x += w + 14
    body += f'<g class="fade" style="animation-delay:.3s">{pills}</g>'
    return card(h, body)


def city(d, stars):
    h = 430
    days = d["days"]
    start = dt.date.fromisoformat(days[0][0])
    offset = (start.weekday() + 1) % 7  # dimanche = 0
    counts = [c for _, c in days]
    mx = max(counts) or 1
    active = sum(1 for c in counts if c)
    busiest = max(counts)

    ux, uy, vx, vy = 9.6, 4.6, -9.0, 4.3      # vecteurs iso semaine / jour
    ox, oy = 392, 118
    cells = []
    for i, (_, c) in enumerate(days):
        k = i + offset
        cells.append((k // 7, k % 7, c))
    cells.sort(key=lambda t: t[0] * uy + t[1] * vy)

    def poly(pts):
        return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)

    def corners(w, dd, s):
        a, b = w + (1 - s) / 2, dd + (1 - s) / 2
        q = lambda m, n: (ox + m * ux + n * vx, oy + m * uy + n * vy)
        return q(a, b), q(a + s, b), q(a + s, b + s), q(a, b + s)

    ground, blds = [], []
    tops = ["#3cc6ae", "#5fdcc4", "#8cf0dc", "#c3fff2"]
    lefts = ["#1d8f7f", "#25a592", "#2fbaa4", "#45cdb7"]
    rights = ["#126a5f", "#167a6d", "#1b8b7c", "#22a08f"]
    for w, dd, c in cells:
        A, B, C, D = corners(w, dd, 1.0)
        ground.append(f'<polygon points="{poly([A, B, C, D])}" fill="#164a45" stroke="#0b302d" stroke-width=".6"/>')
        if not c:
            continue
        r = c / mx
        lvl = min(3, int(r * 4))
        hgt = 8 + 92 * math.sqrt(r)
        A, B, C, D = corners(w, dd, .8)
        up = lambda p: (p[0], p[1] - hgt)
        g = (f'<polygon points="{poly([D, C, up(C), up(D)])}" fill="{lefts[lvl]}"/>'
             f'<polygon points="{poly([B, C, up(C), up(B)])}" fill="{rights[lvl]}"/>'
             f'<polygon points="{poly([up(A), up(B), up(C), up(D)])}" fill="{tops[lvl]}" stroke="#d9fff7" stroke-opacity=".35" stroke-width=".5"/>')
        blds.append(f'<g class="b" style="animation-delay:{.25 + w * .022:.2f}s">{g}</g>')

    css = """
  .b{transform-box:fill-box;transform-origin:50% 100%;animation:grow 1.3s cubic-bezier(.2,.9,.25,1) both}
  @keyframes grow{from{transform:scaleY(.03)}to{transform:scaleY(1)}}
"""
    body = f"""
<g class="fade">
  <text x="60" y="80" class="mono" font-size="11.5" font-weight="700" letter-spacing="3" fill="{MINT}">CONTRIBUTION CITY</text>
  <text x="58" y="130" font-family="{DISPLAY}" font-size="44" font-weight="900" fill="{TEXT}">{d['total']}</text>
  <text x="60" y="154" font-size="14" font-weight="600" fill="{MINT}">contributions in the last year</text>
  <text x="58" y="206" font-family="{DISPLAY}" font-size="30" font-weight="900" fill="{TEXT}">★ {stars}</text>
  <text x="60" y="228" font-size="14" font-weight="600" fill="{MINT}">total stars</text>
  <text x="60" y="268" font-size="13" font-weight="600" fill="{MUTED}">{active} active days</text>
  <text x="60" y="290" font-size="13" font-weight="600" fill="{MUTED}">Busiest day: {busiest}</text>
  <text x="60" y="380" class="mono" font-size="12" fill="{MUTED}">@{escape(d['login'].lower())}</text>
</g>
<g clip-path="url(#pc)">{''.join(ground)}{''.join(blds)}</g>"""
    clip = f'<clipPath id="pc"><rect x="27" y="27" width="{W-54}" height="{h-54}" rx="17"/></clipPath>'
    return card(h, body, extra_defs=clip, extra_css=css)


def population(d, stars):
    h = 280
    tiles = [("Stars", stars, "#5eead4", 50), ("Contributions", d["total"], "#a78bfa", 500),
             ("Repos", d["repo_count"], "#60a5fa", 30), ("Followers", d["followers"], "#22d3ee", 50)]
    tw, gap, x0, y0, th = (W - 92 - 3 * 18) / 4, 18, 46, 120, 120
    body = f"""
<g class="fade">
  <text x="58" y="80" font-family="{DISPLAY}" font-size="30" font-weight="900" fill="{TEXT}">Profile Signal</text>
  <text x="60" y="100" font-size="13" font-weight="700" letter-spacing="1" fill="{MINT}">Live GitHub stats · rebuilt every night</text>
</g>"""
    for i, (lab, val, col, target) in enumerate(tiles):
        x = x0 + i * (tw + gap)
        frac = max(.05, min(1, val / target))
        bw = tw - 44
        body += f"""
<g class="fade" style="animation-delay:{.1 + i * .1:.1f}s">
  <rect x="{x:.1f}" y="{y0}" width="{tw:.1f}" height="{th}" rx="16" fill="#051416" fill-opacity=".85" stroke="#7ef0d8" stroke-opacity=".35"/>
  <text x="{x+22:.1f}" y="{y0+32}" font-size="13" font-weight="800" letter-spacing="1" fill="{MINT}">{lab}</text>
  <text x="{x+20:.1f}" y="{y0+78}" font-family="{DISPLAY}" font-size="38" font-weight="900" fill="{col}">{val}</text>
  <rect x="{x+22:.1f}" y="{y0+94}" width="{bw:.1f}" height="6" rx="3" fill="#1b3537"/>
  <rect x="{x+22:.1f}" y="{y0+94}" width="{bw*frac:.1f}" height="6" rx="3" fill="{col}"/>
</g>"""
    return card(h, body)


def donut(cx, cy, langs, r=26):
    total = sum(s for _, _, s in langs) or 1
    circ = 2 * math.pi * r
    out = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#16343a" stroke-width="7"/>'
    acc = 0.0
    for _, col, s in langs:
        seg = circ * s / total
        out += (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" stroke-width="7" '
                f'stroke-dasharray="{max(seg - 1.2, .6):.2f} {circ:.2f}" stroke-dashoffset="{-acc:.2f}" '
                f'transform="rotate(-90 {cx} {cy})"/>')
        acc += seg
    pct = round(100 * langs[0][2] / total) if langs else 0
    out += f'<text x="{cx}" y="{cy+4}" text-anchor="middle" class="mono" font-size="11" font-weight="700" fill="{TEXT}">{pct}%</text>'
    return out


def landmarks(d):
    repos = [r for r in d["repos"] if not r["archived"] and r["name"].lower() != d["login"].lower()][:MAX_PROJECTS]
    cw, ch, gap = (W - 108 - 24) / 2, 160, 18
    rows = max(1, math.ceil(len(repos) / 2))
    h = 112 + rows * (ch + gap) - gap + 56
    body = f"""
<g class="fade">
  <text x="60" y="72" class="mono" font-size="12" font-weight="700" letter-spacing="3" fill="{MINT}">PROJECTS.LIST</text>
  <text x="210" y="72" class="mono" font-size="12" fill="{MUTED}">./projects.sh --all</text>
  <text x="{W-60}" y="72" text-anchor="end" class="mono" font-size="12" fill="{MUTED}">{len(repos)} projects</text>
  <line x1="54" y1="88" x2="{W-54}" y2="88" stroke="#7ef0d8" stroke-opacity=".35"/>
</g>"""
    for i, r in enumerate(repos):
        x = 54 + (i % 2) * (cw + 24)
        y = 108 + (i // 2) * (ch + gap)
        name = r["name"] if len(r["name"]) <= 24 else r["name"][:23] + "…"
        lang = r["langs"][0][0] if r["langs"] else "—"
        desc = wrap(r["description"] or "No description provided.", 40)
        desc_svg = "".join(
            f'<text x="{x+18:.1f}" y="{y+84+j*16}" class="mono" font-size="11.5" fill="{MUTED}">{escape(t)}</text>'
            for j, t in enumerate(desc))
        lw = text_w(lang, 11, .62) + 22
        body += f"""
<g class="fade" style="animation-delay:{.1 + i * .08:.2f}s">
  <rect x="{x:.1f}" y="{y}" width="{cw:.1f}" height="{ch}" rx="14" fill="#06191b" fill-opacity=".85" stroke="#7ef0d8" stroke-opacity=".4"/>
  <text x="{x+16:.1f}" y="{y+20}" class="mono" font-size="11" fill="{MINT}">▪ {escape(r['name'])}</text>
  <circle cx="{x+cw-18:.1f}" cy="{y+16}" r="4" fill="#3fbf9f" fill-opacity=".8"/>
  <line x1="{x:.1f}" y1="{y+31}" x2="{x+cw:.1f}" y2="{y+31}" stroke="#7ef0d8" stroke-opacity=".3"/>
  <text x="{x+18:.1f}" y="{y+60}" class="mono" font-size="16.5" font-weight="700" fill="{TEXT}">{escape(name)} <tspan fill="{MINT}">_</tspan></text>
  {desc_svg}
  <rect x="{x+18:.1f}" y="{y+112}" width="{lw:.1f}" height="20" rx="10" fill="#0d3332" stroke="#7ef0d8" stroke-opacity=".45"/>
  <text x="{x+29:.1f}" y="{y+126}" class="mono" font-size="11" fill="{MINT}">{escape(lang)}</text>
  <text x="{x+18:.1f}" y="{y+148}" class="mono" font-size="11.5" fill="{MUTED}"><tspan fill="#60a5fa">★</tspan> {r['stars']}   updated {ago(r['pushed'])}</text>
  {donut(round(x+cw-56), y+92, r['langs'])}
</g>"""
    return card(h, body)


def visit():
    h = 160
    items, total = [], 0
    for icon, lab, val in SOCIALS:
        w = max(text_w(val, 13.5, .6), text_w(lab, 11, .6)) + 78
        items.append((icon, lab, val, w))
        total += w
    gap = 16
    total += gap * (len(items) - 1)
    x = (W - total) / 2
    defs = """<linearGradient id="pillg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#103d3a"/><stop offset="1" stop-color="#0a2126"/></linearGradient>"""
    body = ""
    for i, (icon, lab, val, w) in enumerate(items):
        y = 56
        body += f"""
<g class="fade" style="animation-delay:{.1 + i * .08:.2f}s">
  <rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="48" rx="24" fill="url(#pillg)" stroke="#7ef0d8" stroke-opacity=".7" stroke-width="1.5"/>
  <circle cx="{x+26:.1f}" cy="{y+24}" r="15" fill="#1f2e33" stroke="#7ef0d8" stroke-opacity=".35"/>
  <text x="{x+26:.1f}" y="{y+28.5}" text-anchor="middle" font-size="12" font-weight="800" fill="{TEXT}">{escape(icon)}</text>
  <text x="{x+50:.1f}" y="{y+20}" font-size="11" font-weight="800" fill="{MINT}">{escape(lab)}</text>
  <text x="{x+50:.1f}" y="{y+37}" font-size="13.5" font-weight="800" fill="{TEXT}">{escape(val)}</text>
</g>"""
        x += w + gap
    return card(h, body, extra_defs=defs)


# ───────────────────────── MAIN ─────────────────────────
def main():
    d = mock() if "--mock" in sys.argv else fetch()
    stars = sum(r["stars"] for r in d["repos"])
    sizes = {}
    for r in d["repos"]:
        for n, _, s in r["langs"]:
            sizes[n] = sizes.get(n, 0) + s
    langs = sorted(sizes, key=sizes.get, reverse=True)
    os.makedirs(OUT, exist_ok=True)
    for name, svg in [("header", header(d, langs, stars)), ("city", city(d, stars)),
                      ("population", population(d, stars)), ("landmarks", landmarks(d)), ("visit", visit())]:
        with open(os.path.join(OUT, f"{name}.svg"), "w", encoding="utf-8") as f:
            f.write(svg)
        print("wrote", name)


if __name__ == "__main__":
    main()
