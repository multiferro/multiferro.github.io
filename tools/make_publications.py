#!/usr/bin/env python3
"""Build publications.html and the "Recent publications" block of index.html
from publications.bib.

Run from the site root:   python3 tools/make_publications.py

Entries are numbered from the newest (highest number) to the oldest.
Within a year, entries keep the order they have in publications.bib.
No third-party packages are needed.
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIB = ROOT / "publications.bib"
TEMPLATE = ROOT / "tools" / "publications_template.html"
OUT = ROOT / "publications.html"
INDEX = ROOT / "index.html"
RECENT = 5                 # how many papers to show on the home page
HIGHLIGHT = "Lisenkov"     # surname printed in bold in author lists


# ---------------------------------------------------------------- bib parsing
def parse_bib(text):
    entries = []
    pos = 0
    while True:
        m = re.search(r"@(\w+)\s*\{", text[pos:])
        if not m:
            break
        start = pos + m.end()
        depth, i = 1, start
        while depth and i < len(text):
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
        body = text[start:i - 1]
        pos = i
        key, _, rest = body.partition(",")
        fields = {"_type": m.group(1).lower(), "_key": key.strip()}
        j = 0
        while j < len(rest):
            fm = re.match(r"\s*(\w+)\s*=\s*", rest[j:])
            if not fm:
                break
            name = fm.group(1).lower()
            j += fm.end()
            if rest[j] == "{":
                depth, k = 1, j + 1
                while depth:
                    depth += {"{": 1, "}": -1}.get(rest[k], 0)
                    k += 1
                value, j = rest[j + 1:k - 1], k
            elif rest[j] == '"':
                k = rest.index('"', j + 1)
                value, j = rest[j + 1:k], k + 1
            else:
                k = re.search(r"[,\n]", rest[j:])
                k = j + k.start() if k else len(rest)
                value, j = rest[j:k], k
            fields[name] = " ".join(value.split())
            cm = re.match(r"\s*,", rest[j:])
            if cm:
                j += cm.end()
        entries.append(fields)
    return entries


# --------------------------------------------------------- LaTeX -> HTML bits
def math_to_html(m):
    """Convert the inside of $...$ (already HTML-escaped) to HTML."""
    s = m.group(1)
    entities = {}
    def keep(x):                       # protect &gt; &lt; &amp; from the letter logic
        entities[f"\x00{len(entities)}\x00"] = x.group(0)
        return list(entities)[-1]
    s = re.sub(r"&[a-z]+;", keep, s)
    upright = {}
    def mathrm(x):
        upright[f"\x01{len(upright)}\x01"] = x.group(1)
        return list(upright)[-1]
    s = re.sub(r"\\mathrm\{([^}]*)\}", mathrm, s)
    s = re.sub(r"_\{([^}]*)\}", r"<sub>\1</sub>", s)
    s = re.sub(r"_(\x01\d+\x01|\w)", r"<sub>\1</sub>", s)
    s = re.sub(r"\^\{([^}]*)\}", r"<sup>\1</sup>", s)
    s = re.sub(r"\^(\x01\d+\x01|\w)", r"<sup>\1</sup>", s)
    parts = re.split(r"(<[^>]+>)", s)
    for i, p in enumerate(parts):
        if p.startswith("<"):
            continue
        p = re.sub(r"(?<![A-Za-z])([A-Za-z])(?![A-Za-z])", r"<i>\1</i>", p)  # lone letters = variables
        parts[i] = p.replace("-", "&minus;")
    s = "".join(parts)
    for k, v in upright.items():
        s = s.replace(k, v)
    for k, v in entities.items():
        s = s.replace(k, v)
    return s


def latex_to_html(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\$([^$]*)\$", math_to_html, s)
    s = re.sub(r"\\emph\{([^}]*)\}", r"<em>\1</em>", s)
    s = re.sub(r"\\textbf\{([^}]*)\}", r"<b>\1</b>", s)
    s = s.replace("---", "&mdash;").replace("--", "&ndash;")
    s = s.replace("``", "&ldquo;").replace("''", "&rdquo;").replace("\\&amp;", "&amp;")
    s = re.sub(r"[{}]", "", s)
    return s


def format_authors(field):
    names = [n.strip() for n in re.split(r"\s+and\s+", field) if n.strip()]
    out = []
    for n in names:
        n = latex_to_html(n)
        if HIGHLIGHT in n:
            n = f"<b>{n}</b>"
        out.append(n)
    if len(out) <= 2:
        return " and ".join(out)
    return ", ".join(out[:-1]) + ", and " + out[-1]


def link_for(e):
    if e.get("doi"):
        return "https://doi.org/" + e["doi"]
    if e.get("url"):
        return e["url"]
    if e.get("arxiv"):
        return "https://arxiv.org/abs/" + e["arxiv"]
    return None


def render_entry(e, number):
    title = latex_to_html(e.get("title", ""))
    href = link_for(e)
    if href:
        title = f'<a href="{html.escape(href)}">{title}</a>'
    bits = [f'<span class="pub-authors">{format_authors(e.get("author", ""))}</span>,',
            f'<span class="pub-title">&ldquo;{title}&rdquo;</span>,']
    journal = f'<em class="pub-journal">{latex_to_html(e.get("journal", ""))}</em>'
    if e.get("volume"):
        journal += f' <b>{html.escape(e["volume"])}</b>'
    if e.get("pages"):
        journal += f', {html.escape(e["pages"])}'
    journal += f' ({html.escape(e.get("year", ""))}).'
    bits.append(journal)
    if e.get("arxiv") and e.get("doi"):
        bits.append(f'<a class="pub-arxiv" href="https://arxiv.org/abs/{html.escape(e["arxiv"])}">arXiv:{html.escape(e["arxiv"])}</a>')
    return (f'<li class="pub" id="pub-{number}" value="{number}"><div class="pub-body">'
            + " ".join(bits) + "</div></li>")


def main():
    entries = [e for e in parse_bib(BIB.read_text(encoding="utf-8"))
               if e["_type"] in ("article", "inproceedings", "incollection")]
    entries.sort(key=lambda e: -int(e.get("year", 0)))      # stable: keeps file order within a year
    total = len(entries)

    # ---- full list grouped by year
    chunks, number, current = [], total, None
    for e in entries:
        year = e.get("year", "")
        if year != current:
            if current is not None:
                chunks.append("</ol>")
            chunks.append(f'<h2 class="pub-year" id="y{year}">{year}</h2>')
            chunks.append('<ol class="pub-list" reversed>')
            current = year
        chunks.append(render_entry(e, number))
        number -= 1
    chunks.append("</ol>")
    listing = "\n".join(chunks)

    years = sorted({e.get("year", "") for e in entries}, reverse=True)
    year_links = "\n".join(f'      <a href="#y{y}">{y}</a>' for y in years)

    page = TEMPLATE.read_text(encoding="utf-8")
    page = (page.replace("{{PUBLICATIONS}}", listing).replace("{{COUNT}}", str(total))
                .replace("{{YEARS}}", year_links))
    OUT.write_text(page, encoding="utf-8")

    # ---- recent block on the home page
    if INDEX.exists():
        recent = ['<ol class="pub-list pub-list--recent" reversed>']
        for i, e in enumerate(entries[:RECENT]):
            recent.append(render_entry(e, total - i))
        recent.append("</ol>")
        block = "\n".join(recent)
        text = INDEX.read_text(encoding="utf-8")
        new = re.sub(r"(<!-- recent:start -->).*?(<!-- recent:end -->)",
                     lambda m: m.group(1) + "\n" + block + "\n" + m.group(2),
                     text, flags=re.S)
        if new == text and "<!-- recent:start -->" not in text:
            print("warning: index.html has no <!-- recent:start --> ... <!-- recent:end --> markers",
                  file=sys.stderr)
        INDEX.write_text(new, encoding="utf-8")

    print(f"wrote {OUT.name} ({total} entries) and refreshed the recent list in {INDEX.name}")


if __name__ == "__main__":
    main()
